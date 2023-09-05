# Release Notes
Just trying to keep track of changes as they're made.

## Version 1.0.0-RC2
### New features
- Added the ability to set the LACP rate to slow (1 PDU every 30 seconds) for
  devices that can't handle the default 1 pps "fast" rate.  To set the LACP
  rate to slow, simple add the metadata tag `lacp_slow` to the aggregated
  interface where you'd like to apply the setting.

- DHCP server in a routing instance.  This is essential for doing DHCP in an
  EVPN/VXLAN overlay.  Please don't criticize my DHCP server, I know the logic
  is all messed up right now.  But you can at least get addresses from the
  switch that's been declared the DHCP server (declared by applying the tag
  `dhcp_server` to the system) if you're directly attached.  What happens
  beyond that is voodoo right now.  Stay away from the voodoo.

- I'm going to start adding a "Last Updated" comment at the top of files so I
  can keep better track of what changed when.  I'll add the field as I make
  changes to files.

### Changed behavior
- Preparing for Apstra 4.2.0, which will move from Python 2.7 to Python 3.10.
  All the `iteritems` and `itervalues` expressions in the Jinja templates have
  been updated to `items` and `values` respectively.

- Fixed the logic around creating aggregate routes in a routing instance.  You
  don't need to enable static routes in a VRF to get aggregate routes, we just
  want them in the border leafs so we can use them for any routing to the
  outside world.

- Created new import policy `RoutesFromExt-{{ ri['vrf_name'] }}-No_Fabric_Routes`
  that will reject any routes for prefixes that originate in the fabric and
  accepts all other routes.  We will apply this to BGP peers in the VRF(s).

- Created new export policy `RoutesToExt-{{ ri['vrf_name'] }}-Aggregate` that
  will only advertise the aggregate routes configured on each border leaf to
  BGP peers in the VRF(s).  This means that external peers will get visibility
  to the subnets available in the fabric, but not the individual host routes.

- For BGP peering in the VRF(s), we now use the policies above as the default
  import/export policies.  For now, you need to manually change the policies in
  `routing_instances.jinja` if you want the Apstra Default_immutable policies.

- DHCP server/relay is now configured per-VLAN, instead of at the VRF level.
  You will still need the `dhcp_server` tag on the system that acts as the
  DHCP server, but now you can flag the specific VLAN's where you want the
  server to listen.

- Moved the SLAAC and RDNSS config to the VLANs as well.  This makes setting of
  the 'M', 'A', and 'O' flags much easier -- it's all set in the VLAN now.
  
- The 'O' flag in IPv6 router advertisements is now set if either DHCP relay or
  SLAAC is enabled.  Previously the 'O' flag was only enabled with DHCP relay.

### Bug Fixes
- Caught a syntax error in `junos_routing_instances.jinja` that broke the
  config render if DHCP relay was enabled in a routing instance.  This is fixed
  now.

- Fixed the logic around setting the `managed-configuration` and `autonomous`
  flags in IPV6 router advertisements.  We now check to see if the switch is
  configured either as the DHCP server or a DHCP relay in the appropriate
  VRF(s).  Previously we only set the M flag if the switch was a DHCP server.

- Cleaned up a lot of what was in `junos_access.jinja`, `junos_protocols.jinja`,
  and `junos_system.jinja` to reflect that we're now doing DHCP server inside
  the VRF.

## Version 1.0.0-RC1
### New features
None

### Changed behavior
- The default preferences for OSPF and OSPFv3 external routes (150) and EVPN
  routes (170) means that a border leaf will prefer the OSPF route to the EVPN
  route for hosts inside the fabric.  That's bad.  So now we set the preference
  for OSPF external routes to 200 so that the fabric prefers the EVPN route to
  a destination in the fabric.  The preference for OSPF external routes can be
  adjusted from the `protocol_properties` property set.  

- Added OSPF-specific export/import policies to make the situation a bit more
  robust.  The export policy applies a tag to routes exported from the fabric
  via OSPF and OSPFv3, and the import policy rejects routes with those tags
  applied.  So while the switches will use OSPF to route to hosts outside the
  fabric, they will NOT use OSPF/OSPFv3 to route to hosts inside the fabric.

### Bug fixes
- Missed the export policy necessary for OSPF and OSPFv3 to advertise networks
  not configured locally on the device.  Now we advertise all the Type 5 routes
  associated with the routing instance via OSPF(v3).

## Version 0.8.0
### New features
- Added a template called `junos_filter.jinja` where you can create Junos
  firewall filters.  The POC in this case demonstrates "Protect_RE" filters --
  a type of filter applied to the loopback interface (lo0.0) to control
  external interaction with the device control and management planes.  All
  the example filters do is count certain types of traffic destined for the
  device; they don't block anything.  Feel free to populate the template with
  filter(s) of your choosing.

- Related to the `junos_filter.jinja` feature above, `custom_sys_properties`
  now includes a `protect_re:` section where you can enable the Protect-RE
  filter(s) and assign a list of prefixes that are allowed management access
  to the device.

- Support for ND with `onlink-subnet-only`.  Set the flag in 
  `protocol_properties` and then the `junos_protocols.jinja` will render the
  knob accordingly.

- Added support for 802.1X authentication of end users/systems.  Currently
  supports Radius as the authentication method and mac-radius for the
  auth mode.  It supports a single supplicant per switch port, so the first
  "user" to authenticate will determine the state of the port for all other
  users.  You can set the configurable items for 802.1X in under
  `custom_sys_properties`.  If multiple radius servers are configured under the
  `dot1x.radius_servers` key, then their order in the list of servers determines
  what order Junos attemtps to try to authenticate against.  So put your most
  preferred server first, and list them in decreasing order of priority.  You
  can enable 802.1X authentication on a link or aggregate link by assigning the
  metadata tag `dot1x` to the link.

- Added the ability to create firewall filters and apply them to host-facing
  interfaces.  The capability is fairly limited right now.  You create the
  filter by modifying the `filter_properties` property set per the examples
  included in this bundle.  Then you apply the filter to a host-facing link
  or aggregate link by assigning a metadata tag to the link, where the tag is
  the name of the filter you wish to apply.  The filter must be of type
  `family ethernet-switching`, and it is applied in the inbound direction
  only.

### Changed behavior
- Moved all of the sFlow stuff out of `custom_sys_properties` and put it all
  in `protocol_properties` instead.  I've seen the error of my ways...

- Improved the logic around rendering config for host-facing interfaces, where
  we use metadata tags to match and apply config.  We now check to make sure
  the interface is NOT a LAG memeber before applying the config, as LAG members
  should only include config that associates them with an aggregated
  interface.  So if you accidentally apply `mode_trunk` or a VLAN tag to a
  LAG member, it will no longer break the commit on the device, as the config
  assocaited with the tag will not be applied.

### Bug fixes
- Cleaning up the "some platforms don't support sFlow to IPv6 collectors"
  issue.  The `junos_protocols.jinja` template will henceforth not render any
  IPv6-related config if `sflow.source_v6_supported` is false.

- We were performing the checks for DHCP server/relay/none incorrectly, and
  an inconsistent setting across property sets (e.g., `dhcp6_server: enabled` 
  in `custom_sys_properties` and `dhcp6_mode: relay|none` in `vrf_vlan` would
  lead to some vestigal DHCP config in `[edit system services dhcp-local-server]`)
  that broke the commit.  This is fixed now.

- Fixed the logic for assigning the standard MAC address to IRB interfaces with
  anycast addresses assigned.  There was an error in the checks on the IRB
  ifl's that would only assign the MAC to ifl's with an IPv4 anycast assigned.  
  Now we assign the MAC to an ifl with either an IPv4 or IPv6 anycast assigned.

## Version 0.7.0
### New features
- Added support for sflow to an IPv6 target.  The config script will add all
  interfaces connected to external systems to the list of sampled interfaces.
  The collector IP and port are set in `custom_sys_properties` while the 
  polling interval and sample rates are set in `protocol_properties`.  It just
  kind of made sense to me that way. (NOTE:  Not all Junos platforms currently
  support communication with an sFlow collector via IPv6 source address, and
  the QFX5k family is a notable exception.  For this reason, there is a flag
  named `source_v6_supported` under sFlow in the `protocol_properties`
  property set to address this.  It is set to false by default.)

- Added support for SNMP v2.  Handles communities and trap groups, and will
  send all traps via the management VRF.  It will use the IPv6 management
  address, if configured, otherwise the IPv4 address.

- Added support for DHCP relay in the overlay routing instance(s).  Each
  instance can have a maximum of 4 DHCP servers of each v4 and v6.  The
  `vrf_vlan.xlsx` spreadsheet has been updated to support this.  You get a
  Yes/No field for each protocol (e.g., DHCPv4 Relay? and DHCPv6 Relay?) in
  the VRF table, along with fields for up to 4 servers for each protocol.  The
  `parse_vrf_vlan.py` script has also been updated to generate the necessary
  property set to handle this.

- Added basic support for DHCP local server.  This is just for functional
  testing only.  You don't really want to run a DHCP server on your data
  center switch, do you?  There's so much real compute everywhere you look...

### Changed behavior
- For the services defined in `custom_sys_properties`, I've added an "enabled"
  flag to check if the service should be included in the rendered config.
  Doing this means we can keep the configurable items associated with a
  service in the proprerty set (good for examples when we need them) without
  automatically enabling the service.

- Added config to enable gRPC streaming of MAC learning telemetry.  Apstra
  currently collects the data via polling, but future releases will also
  support collection via gRPC streaming telemetry.

- Removing support for symmetric Type 2 for now.  The capability is rolling
  out across platforms in various Junos/Evo releases.  There's a flag in the
  protocol_properties under evpn where we can enable/disable the capbility
  going forward.

- For the purposes of DHCP relay, we need globally unique addresses assigned
  to the loopback interface in each VRF.  This required a bit of a re-thinking
  of how we do IP address assignments for lo0 across the board.  So if you
  want to get relaible addressing on lo0, both for the underlay and in all
  overlay VRF's, you need a resource generator that will allocate loopback
  addresses from an IPv6 resource pool, and set the subnet prefix length in
  the resource generator to a value of 0 < prefix ≤ 112.  Trinying to use
  anything else risks getting collisions on address assignments.

- Re-wrote the `vrf_vxlan` spreadsheet and the associated parser and json
  output.  The VRF info is now separate from the VLAN info, and VLANs are now
  a `member_of` a particular VRF.  This, I hope, will make the spreadsheet
  somewhat more intuitive and manageable.


## Version 0.6.1
### Bug fixes:
- Missing the `virtual-gateway-v4-mac` and `-v6-mac` settings on IRB interfaces
  where we've configured VGA instead of the anycast gateway.  The settings are
  there now.

- Also missing the virtual-gateway-accept-data statement on the IRB interfaces
  where we've comnfigured VGA instead of anycast gw.  Setting has been
  added.

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