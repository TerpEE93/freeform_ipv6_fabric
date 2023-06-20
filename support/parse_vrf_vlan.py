#
# parse_vrf_vlan.py
#   Version 0.5.0
#   This script reads in a properly-formatted Excel spreadsheet named
#   "vrf_vlan.xls" from the local directory and creates a file named
#   "vrf_vlan.json" that can be copied and pasted into the 'vrf_vlan'
#   Property Set in the Apstra Freeform blueprint.  There is an example
#   spreadsheet named "vrf_vlan_example.xls" included in this directory.
#   You may copy that file to a file named "vrf_vlan.xls" in the same
#   directory and make your live edits there.
#
#   Requires:
#   - Python 3.10 or later
#   - Python pandas library
#   - Python json library
#   - Python sys library
#

import pandas as pd
import json as j
import sys

vrf_vlan_dict = {}
vlans = {}
ipv4_prefix_len = ''
irb_gw4 = ''
irb_gw4_a = ''
irb_gw4_b = ''
ipv6_prefix_len = ''
irb_gw6 = ''
irb_gw6_a = ''
irb_gw6_b = ''
is_border = False
is_bgp = False
is_ospf = False
is_static = False
peer_ipv4 = ''
peer_ipv6 = ''
ospf_area = ''
in_file = 'vrf_vlan.xlsx'
in_sheet = 'vrf_vlan_table'
out_file = 'vrf_vlan.json'
err_msg = 'No error message.'
tenant_vni_base = 9000

def errorOut( tenant, vlan, message ):
    print( '\nERROR in tenant ' + tenant + ', VLAN ' + vlan + ':\n' +
           message + '\n\n' )
    sys.exit( -1 )
    return
    
df = pd.read_excel(in_file, sheet_name=in_sheet)

for row in list(range(len( df.index ))):
    s = df.iloc[ row ]
    if pd.notna( s[ 'VRF' ] ):
        tenant = s.loc[ 'VRF' ]
        index = int(s.loc[ 'vrf_index' ])
        tenant_vni = tenant_vni_base + index
        lo0_unit = index
        vrf_name = tenant
        vlans = {}

    elif pd.notna(s[ 'VLAN' ]):
        vlan_id = int( s[ 'vlan_id' ] )
        vxlan_vni = int( index * 10000 + vlan_id )

        if pd.notna( s[ 'ipv4_prefix_len' ] ):
            ipv4_prefix_len = int( s[ 'ipv4_prefix_len' ] )
        else:
            ipv4_prefix_len = ''

        if pd.notna( s[ 'irb_gateway4' ] ):
            irb_gw4 = s[ 'irb_gateway4' ]
        else:
            irb_gw4 = ''

        if pd.notna( s[ 'irb_gateway4_a' ] ):
            irb_gw4_a = s[ 'irb_gateway4_a' ]
        else:
            irb_gw4_a = ''

        if pd.notna( s[ 'irb_gateway4_b' ] ):
            irb_gw4_b = s[ 'irb_gateway4_b' ]
        else:
            irb_gw4_b = ''

        if pd.notna( s[ 'ipv6_prefix_len' ] ):
            ipv6_prefix_len = int( s[ 'ipv6_prefix_len' ] )
        else:
            ipv6_prefix_len = ''

        if pd.notna( s[ 'irb_gateway6' ] ):
            irb_gw6 = s[ 'irb_gateway6' ]
        else:
            irb_gw6 = ''

        if pd.notna( s[ 'irb_gateway6_a' ] ):
            irb_gw6_a = s[ 'irb_gateway6_a' ]
        else:
            irb_gw6_a = ''

        if pd.notna( s[ 'irb_gateway6_b' ] ):
            irb_gw6_b = s[ 'irb_gateway6_b' ]
        else:
            irb_gw6_b = ''

        if s[ 'Border?' ] == 'Yes':
            is_border = True

            if s[ 'BGP?' ] == 'Yes':
                is_bgp = True
                if pd.notna( s[ 'Peer IPv4' ]):
                    peer_ipv4 = s[ 'Peer IPv4' ]
                if pd.notna( s[ 'Peer IPv6' ]):
                    peer_ipv6 = s[ 'Peer IPv6' ]
                if not ( pd.notna( s[ 'Peer IPv4' ]) or
                         pd.notna( s[ 'Peer IPv4' ]) ):
                    err_msg = 'You must have either an IPv4 or IPv6 peer (or both) for BGP peering.'
                    errorOut( tenant, s[ 'VLAN' ], err_msg )
            else:
                is_bgp = False
                
            if s[ 'Static?' ] == 'Yes':
                is_static = True
                if pd.notna( s[ 'Peer IPv4' ]):
                    peer_ipv4 = s[ 'Peer IPv4' ]
                if pd.notna( s[ 'Peer IPv6' ]):
                    peer_ipv6 = s[ 'Peer IPv6' ]
                if not ( pd.notna( s[ 'Peer IPv4' ]) or
                         pd.notna( s[ 'Peer IPv4' ]) ):
                    err_msg = 'You must have either an IPv4 or IPv6 gateway (or both) for a static route.'
                    errorOut( tenant, s[ 'VLAN' ], err_msg )
            else:
                is_static = False
                
            if s[ 'OSPF?' ] == 'Yes':
                is_ospf = True
                if pd.notna( s[ 'OSPF Area' ]):
                    ospf_area = s[ 'OSPF Area' ]
                else:
                    err_msg = 'OSPF = Yes, but no OSPF area set.'
                    errorOut( tenant, s[ 'VLAN' ], err_msg )
            else:
                is_ospf = False
        else:
            is_border = False

        vlans = { **vlans,
                      **{ s[ 'VLAN' ]:{ 'vlan_id':vlan_id,
                                        'vxlan_vni':vxlan_vni,
                                        'ipv4_prefix_len':ipv4_prefix_len,
                                        'irb_gateway4':irb_gw4,
                                        'irb_gateway4_a':irb_gw4_a,
                                        'irb_gateway4_b':irb_gw4_b,
                                        'ipv6_prefix_len':ipv6_prefix_len,
                                        'irb_gateway6':irb_gw6,
                                        'irb_gateway6_a':irb_gw6_a,
                                        'irb_gateway6_b':irb_gw6_b,
                                        'is_border':is_border,
                                        'is_bgp':is_bgp,
                                        'is_static':is_static,
                                        'is_ospf':is_ospf,
                                        'peer_ipv4':peer_ipv4,
                                        'peer_ipv6':peer_ipv6,
                                        'ospf_area':ospf_area } } }

        vrf_vlan_dict.update( { tenant:{ 'vrf_name':tenant,
                                         'tenant_vni':tenant_vni,
                                         'lo0_unit':index,
                                         'vlans':vlans} } )

with open( out_file, 'w' ) as f:
    f.write(j.dumps( vrf_vlan_dict, indent=4 ))
    f.close
