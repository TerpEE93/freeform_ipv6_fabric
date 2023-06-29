# Release Notes
Just trying to keep track of changes as they're made.

## Version 0.6.1
### Bug fixes:
- Missing the virtual-gateway-v4-mac and -v6-mac settings on IRB interfaces
  where we've configured VGA instead of the anycast gateway.

- Also missing the virtual-gateway-accept-data statement on the IRB interfaces
  where we've comnfigured VGA instead of anycast gw.

- Fixed the `default-gateway` setting under `[edit routing-instances VSWITCH protocols evpn]`.  This setting was previously `do-not-advertise` but is now
  set correctly to `no-gateway-community`.

- Added `irb-symmetric-routing` config for the `instance-type vrf` members of
  the overlay domain.  That was missing before.

## Version 0.6.0
### New features:
- Added support for TACACS+ in the `[edit system]` container.  Now you can do
  authentication via RADIUS, TACACS+, or local password.

- Also added support for accounting via RADIUS and TACACS+.  There was already
  support for accounting via SYSLOG (via the authorization, change-log, and
  interactive-command facilities), and now we have better AAA integrations
  too.

- Added support for RNDS service on routed virtual networks.  This is an
  enhancement to the SLAAC support that was added in 0.5.0.

- Added a folder called `json_for_import` which includes the config templates
  exported from Apstra as JSON formatted files.  You can import these files
  into Apstra by clicking the Create Config Template button and then clicking
  the Import Config Template button in the pop-up window.

### Changed behavior:
- Created a new property set called `protocol_properties.json` where we can
  store timer defaults, etc., for use in the `[edit protocols]` and
  `[edit routing-instances <instance> protocols]` containers.  If we need to
  tweak timers, this will make it much easier.

### Bug fixes:
- Apstra and Junos disagree on whether the address <some_prefix>::/<mask> is a
  valid address for a loopback interface, where mask != 127 or 128, so we need
  to make Junos happy.  Now we check the mask assigned to the IPv6 address.
  If the mask is /127 or /128, we leave the Apstra generated address as-is.  If
  the mask is anything else, we set the loopback loopback IPv6 address as
  <some_prefix>::1/<mask>.

## Version 0.5.0
### New features:
- Added support for peering to an external gateway from within a routing zone
  (VRF).  Current support is for BGP, OSPFv2 (for IPv4 networks), OSPFv3
  (for IPv6 networks), and a static default (0.0.0.0/0 for IPv4 and ::/0 for
  IPv6).

- Added an IPv6 address to the ***em0*** interface.  I've highlighted em0 to be
  clear that this is the only interface we handle.  So if your device management
  interface is me0 (EX switches) or fxp0 (vjunos, MX, etc.) this will not work.
  The IPv6 address assigned to the em0 interface comes from the variable
  `mgt_prefix_v6` defined in the `custom_sys_properties.json` prepended to the
  IPv4 address rendered by Apstra as the `management_ip` in the device context.
  So you don't get to pick right now; you get what you get...

- Also added a default IPv6 route ( ::/0 ) to the mgmt_junos routing instance
  that points to a next-hop of `{{ mgt_prefix_v6 }}::1`.  Again, you don't get
  to pick right now...

- SLAAC is now supported on routed virtual networks (think VLAN with an IRB
  interface).

- The `[edit system]` capabilities from version 0.3.0 now support declaring
  the IPv6 address associated with em0.0 as the source for these capabilities.

### Changed behavior:
- Updated the junos_policy_options.jinja file to better match how the reference
  design policies handle advertising IPv4 and IPv6 networks.  The policies
  for the routing instances now enable Type 5 advertisements by default, and
  can handle redistribution from OSPF and static routes.

- To implement the change above, added several new columns to the spreadsheet
  vrf_vlan_example.xlsx.  There's a Yes/No to determine if if VLAN is a border
  VLAN (e.g., has a protocol peering to an external gateway), and then several
  checks for BGP/OSPF/Static route peering.  For BGP and Static, the user
  should include a peer from the appropriate address family.  For OSPF, the
  user should include the OSPF Area ID.  There are rudimentary checks for peers
  and OSPF are in the parse_vrf_vlan.py script.

### Bug fixes:
- Previous releases set the protocol MTU for IRB interfaces incorrectly at the
  `[edit interfaces irb]` level.  This needed to be moved into the protocol
  families instead (e.g., `[edit interfaces irb unit 99 family inet]`).  That
  issue is now fixed.

## Version 0.4.1
### Changed behavior:
- Just a change to .gitignore so that we no longer include the vrf_vlan.json
  and vrf_vlan.xlsx files from the support/ directory.  These are actual
  working files, and they change whenever I run a test.  Now we just include
  the example spreadsheet to avoid confusion.

## Version 0.4.0
### New features:
- Adding support for peering to external gateways.  This has forced more changes
  to how the `vrf_vlan` property set is setup, as well as the example
  spreadsheet and the `parse_vrf_vlan.py` conversion tool.  See the
  **Changed behavior** section for details.  Support for peering allows for
  peering from the unique address of the IRB on a border leaf to a peer IP
  address.  This capability currently supports:
    * External BGP
    * OSPFv2
    * OSPFv3
  __This does not work yet.  The templating work to build the IRB interfaces
  in the external-facing VLAN is complete - we're using VGA vs. anycast
  addresses in this case - but the routing work is still to be done.

### Changed behavior:
- The `vrf_vlan` property set used to provide IPv4 and IPv6 prefix assignements
  (e.g., 172.31.99.1/24) for the default gateway associated with a VLAN.
  While this was fine for anycast gateways, things are a bit more complicated
  when we need both a virtual gateway address and unique addresses per system.
  So the original `irb_prefix4` has been replaced with `ipv4_prefix_len`
  (the length of the subnet mask), `irb_gateway4` (the virtual gateway address),
  and `irb_gateway4_a` and `irb_gateway4_b` (which are the unique IP addresses
  assigned to the gateways, up to 2).  Similar changes have been made to
  replace the `irb_prefix6` assignment.

### Bug fixes:
- None

## Version 0.3.0
### New features:
- Support for a richer `[edit system]` container.  Current support for:
    * The domain-name command
    * List of DNS servers
    * List of NTP servers
    * Support for RADIUS authentication and setting the authentication-order
    * Syslog to both file and host targets

Note that you can set the management VRF name in the custom_sys_properties
file, but it should be left as `mgmt_junos` if you want management functions
to work properly...

### Bug fixes:
None in this release, thought we've likely introduced a few new ones :)

## Version 0.2.1
### Changed behavior:
- Previous releases of this tool-set supported VXLANs that were one of pure-L2,
  IPv4 only, or IPv6 only.  Missing was support for a dual-stack VXLAN.  That
  is corrected in this release.

- To support the change above (dual-stack VXLANs), the `vrf_vlan` property set
  has been changed.  What was previously called `irb_prefix`, with prefix-mask
  guesses as to whether it was an IPv4 prefix (mask < 32) or an IPv6 prefix
  (mask >= 32) has been removed.  From this release forward, we introduce
  `irb_prefix4` for IPv4 VXLAN prefixes and `irb_prefix6` for IPv6 VXLAN
  prefixes.  Updates have been made to the necessary configuration templates,
  the Python tool `parse_vrf_vlan.py`, and the example spreadsheet.

- The vrf_vlan_example spreadsheet included in the support/ directory is now
  formatted as an .xlsx workbook rather than the older .xls format.  Copy the
  example file to `vrf_vlan.xlsx` and make your edits there.  There is a sheet
  of instructions included in the workbook. 

- The Apstra 4.1.2 reference design sets every L2 port as an edge port under
  `[edit protocols rstp]`.  Updated the `junos_protocols.jinja` to do the
  same thing here.

### Bug fixes:
- The `junos_protocols.jinja` template was creating entries for IPv4-only
  IRB interfaces under the `[edit protocols router-advertisement]` container.
  This was not correct.  The template has been updated so that only IRB
  interfaces with an IPv6 address assigned are included in this configuration
  container.  (This change includes IPv6-only and dual-stack IRB interfaces.)

## Version 0.2.0
New features:
- Added a python script in the `support` folder that will convert a properly-
  formatted Excel spreadsheet of Tenant/VLAN entries into JSON that can be
  pasted into the `vrf_vlan` Property Set in the blueprint.  There is an
  example spreadsheet included in the folder as well.

Changed behavior:
- What was previously called `ip_prefix` in the Configuration Templates and
  Property Sets has been renamed `irb_prefix` for clarity, as the only place
  we used `ip_prefix` was to associate IP addresses with the IRB interfaces.

Big fixes:
- TBD

## Version 0.1.3
Bug fixes only:
- Removed `vrf-target auto` from the configuration of the VSWITCH instance
  generated by the `junos_routing_instances.jinja` template.
- Along those lines... We now allocate route targets per VNI in the VSWITCH
  instance.  Updated the config in the `junos_routing_instances.jinja` template.
- Completely missed the `junos_system.jinja` file.  It's included in the
  package now.
- A routing instance of type mac-vrf must have interfaces attached to the
  virtual switching instance.  If a leaf device was provisioned without host
  interfaces (e.g., just setting up the fabric-facing interfaces), then the
  commit would fail.  Updated `junos_routing_instances.jinja` to make sure
  VLANs are applied to host interfaces on leaf devices before building out
  the VSWITCH routing instance, since that is our mac-vrf instance.
- Fixed `junos_protocols.jinja` so that we only configure IRB interfaces
  under `[edit protocols router-advertisement ]` if the IRB is configured
  on the device.

## Version 0.1.2
Bug fixes only:
- The template for the `BGP-AOS-Policy` was missing term 20, which matched
  on protocol BGP and accepted the routes.  This was preventing spine
  devices from forwarding BGP-learned routes between leafs.
- Cleaned up the resrouce generators to use `lacp_system_ids` for both the
  ESI and LACP system ID values on a LAG bundle.  The old ESI generator
  was still being used in the interface template to generate the ESI value
  on the LAG, and the check was failing (since the resource generator no
  longer existed).  ESI values are now properly generated from the
  `lacp_system_ids` resource generator.

## Version 0.1.1
Bug fixes only:
- Fixed closing braces on LAG member interfaces (one closing brace was missing).
- Added host-facing interfaces to the mac-vrf (virtual switch) instance under
  the `[edit routing-instances]` container on leaf devices.
- Added loopback interfaces to the L3 (instance-type vrf)routing instances.
  These lo0 interfaces use link-local scoped addresses only.  They are
  necessary for protocol support in the routing instance.  These were
  previously missing.
- Added the IRB interfaces in each L3 instance under the
  [ edit prototocl router-advertisement ] container.  These were previously
  missing.
- Moved replace: tag on routing-instances from the top of the container
  to the individual routing instances.  Oops, I wiped out mgmt_junos...
- Added the `default-gateway do-not-advertise` and `extended-vni-list all`
  statements under the `[edit routing-instances VSWITCH protcols evpn]`
  container.
- VLANs and their associated IRB interfaces are only generated on the devices
  where the VLANs are applied.
- Setting the MAC address on the IRB interfaces consistent with the setting
  in the Apstra reference design.

## Version 0.1
Initial release.  Deploys a 3-stage fabric with an IPv6-only underlay, to
include all fabric links and loopback interfaces.  The overlay VXLANs can
be L2-only, IPv4 edge-routed, or IPv6 edge-routed.