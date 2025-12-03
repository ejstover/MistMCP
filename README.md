# Mist MCP

Model Context Protocol (MCP) server for Juniper Mist automation. The server exposes tools to search for devices, answer site questions, and apply specific port profiles to switch ports using the Mist API. Environment variables are loaded from a `.env` file so credentials are not stored in code.

## Quick start
1. Copy `.env.example` to `.env` and fill in your Mist API values:
   - `MIST_API_TOKEN` – personal access token
   - `MIST_ORG_ID` – organization ID to query
   - `MIST_API_BASE_URL` – Mist API base URL (defaults to the public cloud)
   - `MIST_DEFAULT_SITE_ID` – optional fallback site
2. Install dependencies: `pip install .`
3. Run the MCP server module (Python's `-m` flag runs `src/mist_mcp/server.py`): `python -m mist_mcp.server`

## Using with Claude
To connect this MCP server to Claude Desktop:
1. Complete the quick start steps and ensure `.env` contains your Mist credentials.
2. Open Claude Desktop settings and add a new MCP server entry pointing to this project. A JSON example for `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "mist-mcp": {
         "command": "python",
         "args": ["-m", "mist_mcp.server"],
         "cwd": "/path/to/MistMCP",
         "envFile": "/path/to/MistMCP/.env"
       }
     }
   }
   ```
3. Save the configuration and restart Claude Desktop so it loads `mist-mcp` with your environment file.

## How to use the MCP server
Once connected (for example via Claude Desktop), you can prompt the MCP server with natural language. Here are practical prompts a network engineer might use:

- Inventory lookups
  - "Find the device with IP `10.10.5.12` and tell me its hostname and site."
  - "Search for MAC `b8:27:eb:12:34:56` and include the serial number."
  - "Locate hostname `core-switch-3` in the org and show the model."
  - "Find the client using IP `10.0.0.150` and tell me which AP it is on."
  - "Who is using MAC `aa:bb:cc:dd:ee:ff` right now and what site are they at?"
  - "Look up the wireless client named `lab-laptop-01` and include VLAN and AP details."
  - "How many APs are connected today, how many are offline, and how many are still in-stock (never connected)? Include counts by model."
- Site insights
  - "List all sites in Germany and the Netherlands."
  - "How many switches and APs are at the site `HQ-Berlin`?"
  - "Which sites in the last 30 minutes have alarms or errors?"
- Change management (write actions)
  - "On switch `00:11:22:33:44:55`, apply port profile `AP-Uplink` to port `ge-0/0/5`."
  - "Create a new site named `Remote-Branch-42` in country code `US` with timezone `America/New_York` and address `123 Main St, Springfield`."
- Subscriptions
  - "Summarize our subscriptions—totals, used, available, and the next renewal date."
  - "List every subscription SKU with counts and usage."

> Tip: Include site IDs or names when you want to scope results. The tools are read-only except where explicitly noted (port profile updates and site creation).

## Tools
- **find_device** – search inventory by IP address, MAC address, or hostname. Optionally limit to a site.
- **find_client** – search connected or historical clients by IP address, MAC address, or hostname. Optionally limit to a site.
- **list_sites** – list sites, optionally filtered by country codes.
- **site_device_counts** – summarize device counts (switches, APs, etc.) for a site.
- **sites_with_recent_errors** – return alarms for one or more sites within the last N minutes.
- **configure_switch_port_profile** – apply a specific port profile to a switch port on a device.
- **create_site** – provision a new Mist site (requires `name`, `country_code`, `timezone`, and `address`).
- **subscription_summary** – report subscription counts, usage, next renewal, and raw subscription details.
- **inventory_status_summary** – report total, connected, disconnected, and in-stock device counts by model. Accepts optional `site_id` and `device_types` (e.g., `ap` or `switch`).
- **list_guest_authorizations** – list all guest authorizations in the org.
- **list_site_networks** – list derived networks for a site.
- **site_port_usages** – fetch derived port usages from site settings to choose the correct switch profile.
- **acknowledge_all_alarms** – acknowledge every alarm at a site.
- **acknowledge_alarms** – acknowledge multiple specified alarms at a site.
- **acknowledge_alarm** – acknowledge a specific alarm at a site.

## Prompts
`prompts/list` will show the registered helpers you can call directly instead of crafting custom requests:

- **inventory_overview_prompt** – calls `inventory_status_summary`. Inputs: optional `site_id` and `device_types` (list such as `["ap", "switch"]`).
- **device_lookup_prompt** – calls `find_device`. Inputs: `identifier` (IP, MAC, or hostname) and optional `site_id`.
- **client_lookup_prompt** – calls `find_client`. Inputs: `identifier` (IP, MAC, or hostname) and optional `site_id`.
- **list_sites_prompt** – calls `list_sites`. Inputs: optional `country_codes` array (e.g., `["DE", "NL"]`).
- **site_errors_prompt** – calls `sites_with_recent_errors`. Inputs: `minutes` window plus optional `site_ids` array or `country_codes`.

## Design notes
- Requests are routed through a tiny Mist client wrapper that handles authentication and optional site defaults.
- Write operations (like applying a port profile or creating a site) rely on Mist REST API PUT/POST endpoints.
- Additional tools can be layered onto the same `FastMCP` server in the future.
