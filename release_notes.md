# Release Notes
Just trying to keep track of changes as they're made.

## Version 0.1.1
Bug fixes only:
- Fixed closing braces on LAG member interfaces (one closing brace was missing).
- Added host-facing interfaces to the mac-vrf (virtual switch) instance under
  the [edit routing-instances] container on leaf devices.
- Added loopback interfaces to the L3 (instance-type vrf)routing instances.
  These lo0 interfaces use link-local scoped addresses only.  They are
  necessary for protocol support in the routing instance.  These were
  previously missing.
- Added the IRB interfaces in each L3 instance under the
  [ edit prototocl router-advertisement ] container.  These were previously
  missing.
- Moved replace: tag on routing-instances from the top of the container
  to the individual routing instances.  Oops, I wiped out mgmt_junos...
- Added the "default-gateway do-not-advertise" and "extended-vni-list all"
  statements under the [edit routing-instances VSWITCH protcols evpn]
  container.
- VLANs and their associated IRB interfaces are only generated on the devices
  where the VLANs are applied.
- Setting the MAC address on the IRB interfaces consistent with the setting
  in the Apstra reference design.

## Version 0.1
Initial release.  Deploys a 3-stage fabric with an IPv6-only underlay, to
include all fabric links and loopback interfaces.  The overlay VXLANs can
be L2-only, IPv4 edge-routed, or IPv6 edge-routed.