# freeform_ipv6_fabric
Apstra Freeform desgn to deploy an EVPN-VXLAN overlay on an IPv6-only underlay

Built from Apstra 4.1.2

See the HOWTO doc for how to create a Freeform blueprint to utilize this
package correctly.  The config templates expect that the Allocation pools
and Resource Management are setup correctly.

There is no warranty, expressed or implied, with this repo. You get what you
pay for, and what you see here is free. Use carefully, and at your own risk.

To Do:
- Create allocation pools to dynamically generate and assign VNI's in
  the same manner we do for ASN's and IP addresses.
- Better data validation and assorted error checking.
- Clean up some of the strange whitespace in the rendered configs.  Where
  I append values to a list in a Jinja template, I get blank lines right now.
- Other stuff I'm not thinking of right now...