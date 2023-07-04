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

# Things you might want to change
in_file = 'vrf_vlan.xlsx'       # Excel file to read in
vrf_in_sheet = 'vrf_table'      # Sheet in Excel file with the VRF data
vlan_in_sheet = 'vlan_table'    # Sheet in Excel file with the VLAN data
out_file = 'vrf_vlan.json'      # JSON file we write out
vrf_vni_base = 9000             # The VRF VNI is this + the VRF index

# Don't change these
vrf_list = [ ]
vlan_list = [ ]
vrf_vlan = { }
result = False
err_msg = 'No error message.'

def errorOut( vrf_name, vlan, message ):
    print( '\nERROR in tenant ' + vrf_name + ', VLAN ' + vlan + ':\n' +
           message + '\n\n' )
    sys.exit( -1 )
    return

def gen_vrf_list( vrf_dataframe ):
    df = vrf_dataframe
    dhcp4_server_list = [ ]
    dhcp6_server_list = [ ]
    vrf_list_of_dict = [ ]
    index = ''
    is_dhcp4_relay = False
    is_dhcp6_realy = False
    lo0_unit = ''
    ospf_area = ''
    vrf_index = ''
    vrf_name = ''

    for row in list(range(len( df.index ))):
        s = df.iloc[ row ]
        if pd.notna( s[ 'VRF' ] ):
            vrf_name = s.loc[ 'VRF' ]
            index = int(s.loc[ 'VRF Index' ])
            lo0_unit = index
            vrf_index = vrf_vni_base + int(index)

            if pd.notna( s[ 'OSPF Area' ] ):
                ospf_area = s[ 'OSPF Area' ]
            else:
                ospf_area = ''
            
            if s.loc[ 'DHCPv4 Relay?' ] == 'Yes':
                is_dhcp4_relay = True
                if pd.notna( s.loc[ 'DHCPv4 Server 1' ] ):
                    dhcp4_server_list.append( s.loc[ 'DHCPv4 Server 1' ] )
                if pd.notna( s.loc[ 'DHCPv4 Server 2' ] ):
                    dhcp4_server_list.append( s.loc[ 'DHCPv4 Server 2' ] )
                if pd.notna( s.loc[ 'DHCPv4 Server 3' ] ):
                    dhcp4_server_list.append( s.loc[ 'DHCPv4 Server 3' ] )
                if pd.notna( s.loc[ 'DHCPv4 Server 4' ] ):
                    dhcp4_server_list.append( s.loc[ 'DHCPv4 Server 4' ] )

            if s.loc[ 'DHCPv6 Relay?' ] == 'Yes':
                is_dhcp6_realy = True
                if pd.notna( s.loc[ 'DHCPv6 Server 1' ] ):
                    dhcp6_server_list.append( s.loc[ 'DHCPv6 Server 1' ] )
                if pd.notna( s.loc[ 'DHCPv6 Server 2' ] ):
                    dhcp6_server_list.append( s.loc[ 'DHCPv6 Server 2' ] )
                if pd.notna( s.loc[ 'DHCPv6 Server 3' ] ):
                    dhcp6_server_list.append( s.loc[ 'DHCPv6 Server 3' ] )
                if pd.notna( s.loc[ 'DHCPv6 Server 4' ] ):
                    dhcp6_server_list.append( s.loc[ 'DHCPv6 Server 4' ] )

        vrf_list_of_dict.append( {
                            'vrf_name': vrf_name, 'vrf_index': vrf_index,
                            'lo0_unit': lo0_unit, 'ospf_area': ospf_area,
                            'is_dhcp4_relay': is_dhcp4_relay,
                            'is_dhcp6_relay': is_dhcp6_realy,
                            'dhcp4_servers': dhcp4_server_list,
                            'dhcp6_servers': dhcp6_server_list
                          } )
    
    # End of 'for row in list(range(len( df.index ))):'

    return( vrf_list_of_dict )

def gen_vlan_list( vlan_dataframe ):
    df = vlan_dataframe
    vlan_list_of_dict = [ ]
    ipv4_pref_len = ''
    ipv6_pref_len = ''
    irb_gw4 = ''
    irb_gw4_a = ''
    irb_gw4_b = ''
    irb_gw6 = ''
    irb_gw6_a = ''
    irb_gw6_b = ''
    is_border = False
    is_bgp = False
    is_ospf = False
    is_static = False
    peer_ipv4 = ''
    peer_ipv6 = ''
    bgp_peer_asn = ''
    member_of = ''
    vlan_id = ''
    vlan_name = ''

    for row in list(range(len( df.index ))):
        s = df.iloc[ row ]
        if pd.notna( s[ 'VLAN' ] ):
            vlan_name = s[ 'VLAN' ]
            vlan_id = int( s[ 'vlan_id' ] )
            vxlan_vni = int( 10000 + vlan_id )

            if pd.notna( s[ 'vrf' ] ):
                member_of = s[ 'vrf' ]
            else:
                err_msg = 'This VLAN is not assigned to a VRF.'
                errorOut( vlan_name, err_msg )


            if pd.notna( s[ 'ipv4_prefix_len' ] ):
                ipv4_pref_len = int( s[ 'ipv4_prefix_len' ] )
            else:
                ipv4_pref_len = ''

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
                ipv6_pref_len = int( s[ 'ipv6_prefix_len' ] )
            else:
                ipv6_pref_len = ''

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
                        errorOut( 'None', s[ 'VLAN' ], err_msg )
                    if pd.notna( s[ 'BGP Peer ASN' ] ):
                        bgp_peer_asn = int( s[ 'BGP Peer ASN' ] )
                    else:
                        err_msg = 'You must define the peer ASN for BGP.'
                        errorOut( 'None', s[ 'VLAN' ], err_msg )
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
                        errorOut( 'None', s[ 'VLAN' ], err_msg )
                else:
                    is_static = False
                
                if s[ 'OSPF?' ] == 'Yes':
                    is_ospf = True        
            else:
                is_border = False
            
            # End of 'if s[ 'Border?' ] == 'Yes':'
        # End of 'if pd.notna( s[ 'VLAN' ] ):'

        vlan_list_of_dict.append( {
                            'vlan_name': vlan_name,
                            'vlan_id': vlan_id,
                            'vxlan_vni': vxlan_vni,
                            'member_of': member_of,
                            'ipv4_prefix_len':ipv4_pref_len,
                            'irb_gateway4':irb_gw4,
                            'irb_gateway4_a':irb_gw4_a,
                            'irb_gateway4_b':irb_gw4_b,
                            'ipv6_prefix_len':ipv6_pref_len,
                            'irb_gateway6':irb_gw6,
                            'irb_gateway6_a':irb_gw6_a,
                            'irb_gateway6_b':irb_gw6_b,
                            'is_border':is_border,
                            'is_bgp':is_bgp,
                            'is_static':is_static,
                            'is_ospf':is_ospf,
                            'peer_ipv4':peer_ipv4,
                            'peer_ipv6':peer_ipv6,
                            'bgp_peer_asn':bgp_peer_asn
                            } )
        
    # End of 'for row in list(range(len( df.index ))):'

    return( vlan_list_of_dict )

def sanity_checks( vrf_list, vlan_list ):
    vr = vrf_list
    vl = vlan_list
    vr_names = [ ]

    vr_names = [ item['vrf_name'] for item in vr]

    for vlan in vl:
        if vlan['member_of'] not in vr_names:
            err_msg = 'VLAN ' + vlan['vlan_name'] + ' not associated with VRF in list ' + vr_names
            errorOut( 'None', vlan['vlan_name'], err_msg )
    
    return( True )


print( 'Reading in data...' )    
df_vrf = pd.read_excel(in_file, sheet_name=vrf_in_sheet)
df_vlan = pd.read_excel(in_file, sheet_name=vlan_in_sheet)

vrf_list = gen_vrf_list( df_vrf )
vlan_list = gen_vlan_list( df_vlan )

print( 'Perfroming basic sanity checks...' )
result = sanity_checks( vrf_list, vlan_list )

if result:
    print( 'Writing json to ' + out_file + '...')
    vrf_vlan = { 'vrfs':vrf_list, 'vlans':vlan_list }

    with open( out_file, 'w' ) as f:
        f.write(j.dumps( vrf_vlan, indent=4 ))
        f.close
