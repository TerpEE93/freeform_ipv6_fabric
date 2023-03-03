# HOWTO
Here are the basic elements to make the magic happen...

1.  Lay out your systems in the editor.
    - Create internal systems for the switches that Apstra will manage.
    - Create external systems for hosts and other devices that will connect
      to the edge of the fabric.
    - Apply system tags to the internal systems to identify leaf and spine
      devices.  These tags should be named "leaf" for leaf devices and
      "spine" for spine devices.

2.  Connect your devices.
    - Fabric links must include the tag "fab_link".
    - Host-facing links must include either the "mode_access" or
      "mode_trunk" tags to differentiate untagged vs. tagged interfaces.
    - Tag the host-facing links with tags to represent the VLANs you
      want assigned to each host-facing link.  So if you're going to name
      a VLAN "vlan_100" in your property set (we'll discuss that later on),
      then you need a tag named "vlan_100" applied to the appropriate
      host interface.
    
    NOTE:  Where you have Link Aggregation Goups (LAGs) composed of one
           or more member links, the tags must be applied to the Aggregated
           link, and not the member links.

3.  Create the following Allocation Groups to be used in the model:
    - "ASN Pool" of Type ASN
        This is what we'll use to dynamically assign ASN's to each
        internal system.
    - "Loopbacks" of Type IPv6
        Used to generate IPv6 addresses for lo0.0 on each internal system.
    - "Fabric Links" of Type IPv6
        Used to generate IPv6 addresses for the fabric interfaces.
    - "RIDv4" of Type IPv4
        Used to generate 32-bit router ID's for each internal system.
    - "esi_ids" of Type Integer
        Use low values for integers (e.g., 1-4094).  We'll use these values
        to generate ESI and LACP System ID values.

4.  Under Resource Management, create the following:
    - Group named "fabric_resources" under Root.
    - Group named "lacp" under Root.
    - Group generator named "devices" under fabric_resources.
        Scope: node('system', system_type='internal', name='target')
    - Resource generator named "asn_assignments" under
      Root/fabric_resources/devices
        - Scope:  node('system', system_type='internal', name='target')
        - Allocation Group:  ASN Pool
    - Resource generator named "loopback_assignments" under
      Root/fabric_resources/devices
        - Scope:  node('system', system_type='internal', name='target')
        - Allocation Group:  Loopbacks
    - Resource generator named "router_id" under Root/fabric_resources/devices
       -  Scope:  node('system', system_type='internal', name='target')
        - Allocation Group:  RIDv4
    - Resource generator named "Fabric Link Addressing" under
      Root/fabric_resources
        - Scope:  node('link', role='internal', name='target')
        - Allocation Group:  Fabric Links
    - Resource generator named "lacp_system_ids" under Root/lacp
        - Scope:
            match(
                node('system', name='system', system_type='internal')
                    .out('hosted_interfaces')
                    .node('interface', if_type='port_channel', name='system_interface')
                    .in_('composed_of')
                    .node('interface', name='target')
            )
        - Allocation group:  esi_ids

5.  Now import the Config Templates and Property Sets from this repo.
    You will need to edit the property sets for your specific blueprint.
    - interface_properties: Set MTU for fabric interfaces, host interfaces,
        and IRB interfaces.
    - vrf_vlan: Define the routing zones (VRF) and VLAN's assigned to each.

6.  At this point, you should be able to generate configs.  I strongly
    suggest testing via the <copy>:load replace terminal:<paste> method to
    start.  Once you're confident that the configs are being generated
    correctly, you can push the commit through Apstra.


GOOD LUCK!!!
    