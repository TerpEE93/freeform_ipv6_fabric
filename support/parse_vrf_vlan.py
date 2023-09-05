#
# parse_vrf_vlan.py
#   Version 1.0.0-RC2
#   Last updated 1 Sept 2023 at 15:45 EDT
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
    vrf_list_of_dict = [ ]
    index = ''
    lo0_unit = ''
    ospf_area = ''
    vrf_name = ''
    vrf_vni = ''

    for row in list(range(len( df.index ))):
        s = df.iloc[ row ]
        if pd.notna( s[ 'VRF' ] ):
            vrf_name = s.loc[ 'VRF' ]
            index = int(s.loc[ 'VRF Index' ])
            lo0_unit = index
            vrf_vni = vrf_vni_base + int(index)

            if pd.notna( s[ 'OSPF Area' ] ):
                ospf_area = s[ 'OSPF Area' ]
            else:
                ospf_area = ''
            
        vrf_list_of_dict.append( {
                            'vrf_name': vrf_name,
                            'vrf_vni': vrf_vni,
                            'lo0_unit': lo0_unit,
                            'ospf_area': ospf_area
                          } )
    
    # End of 'for row in list(range(len( df.index ))):'

    return( vrf_list_of_dict )

def gen_vlan_list( vlan_dataframe ):
    df = vlan_dataframe
    vlan_list_of_dict = [ ]

    for row in list(range(len( df.index ))):
        dhcp4_mode = ''
        dhcp4_server = ''
        dhcp4_low = ''
        dhcp4_high = ''
        dhcp6_mode = ''
        dhcp6_server = ''
        dhcp6_low = ''
        dhcp6_high = ''
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
        is_slaac = False
        is_ra_other = False
        is_rdnss = False
        rdnss_server = ''

        peer_ipv4 = ''
        peer_ipv6 = ''
        bgp_peer_asn = ''
        member_of = ''
        vlan_id = ''
        vlan_name = ''

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

            if pd.notna( s[ 'irb_gateway4' ] ):
                irb_gw4 = s[ 'irb_gateway4' ]

            if pd.notna( s[ 'irb_gateway4_a' ] ):
                irb_gw4_a = s[ 'irb_gateway4_a' ]

            if pd.notna( s[ 'irb_gateway4_b' ] ):
                irb_gw4_b = s[ 'irb_gateway4_b' ]

            if pd.notna( s[ 'ipv6_prefix_len' ] ):
                ipv6_pref_len = int( s[ 'ipv6_prefix_len' ] )

            if pd.notna( s[ 'irb_gateway6' ] ):
                irb_gw6 = s[ 'irb_gateway6' ]

            if pd.notna( s[ 'irb_gateway6_a' ] ):
                irb_gw6_a = s[ 'irb_gateway6_a' ]

            if pd.notna( s[ 'irb_gateway6_b' ] ):
                irb_gw6_b = s[ 'irb_gateway6_b' ]

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
                
                if s[ 'OSPF?' ] == 'Yes':
                    is_ospf = True        
            # End of 'if s[ 'Border?' ] == 'Yes':'

            if ( pd.notna( s['SLAAC?'] ) and 
                 ( s['SLAAC?'] == 'Yes' or s['SLAAC?'] == 'Yes+Other' ) ):
                is_slaac = True

                if ( pd.notna( s['RDNSS?'] ) and 
                     s['RDNSS?'] == 'Yes' and
                     pd.notna( s['RDNSS Server'] ) and
                     s['RDNSS Server'] != ''):
                    is_rdnss = True
                    rdnss_server = s['RDNSS Server']

                if s['SLAAC?'] == 'Yes+Other' and not is_rdnss:
                    is_ra_other = True

            if pd.notna( s['DHCPv4 Mode'] ): 
                if ( s['DHCPv4 Mode'] == 'Server' and
                     pd.notna( ['DHCPv4 Low'] ) and
                     s['DHCPv4 Low'] != '' and
                     pd.notna( s['DHCPv4 High'])  and
                     s['DHCPv4 High'] != '' ):
                        dhcp4_mode = 'server'
                        dhcp4_low = s[ 'DHCPv4 Low' ]
                        dhcp4_high = s[ 'DHCPv4 High' ]

                elif ( s['DHCPv4 Mode'] == 'Relay' and
                       pd.notna( s['DHCPv4 Server'] ) and
                       s['DHCPv4 Server'] != '' ):
                        dhcp4_mode = 'relay'
                        dhcp4_server = s['DHCPv4 Server']

                else:
                    dhcp4_mode = 'none'

            if pd.notna( s['DHCPv6 Mode'] ): 
                if ( s['DHCPv6 Mode'] == 'Server' and
                     pd.notna( ['DHCPv6 Low'] ) and
                     s['DHCPv6 Low'] != '' and
                     pd.notna( s['DHCPv6 High'])  and
                     s['DHCPv6 High'] != '' ):
                        dhcp4_mode = 'server'
                        dhcp4_low = s[ 'DHCPv6 Low' ]
                        dhcp4_high = s[ 'DHCPv6 High' ]

                elif ( s['DHCPv6 Mode'] == 'Relay' and
                       pd.notna( s['DHCPv6 Server'] ) and
                       s['DHCPv6 Server'] != '' ):
                        dhcp4_mode = 'relay'
                        dhcp4_server = s['DHCPv6 Server']

                else:
                    dhcp6_mode = 'none'
           
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
                            'bgp_peer_asn':bgp_peer_asn,
                            'is_slaac': is_slaac,
                            'is_ra_other': is_ra_other,
                            'is_rdnss': is_rdnss,
                            'rdnss_server': rdnss_server,
                            'dhcp4_mode': dhcp4_mode,
                            'dhcp4_server': dhcp4_server,
                            'dhcp4_low': dhcp4_low,
                            'dhcp4_high': dhcp4_high,
                            'dhcp6_mode': dhcp6_mode,
                            'dhcp6_server': dhcp6_server,
                            'dhcp6_low': dhcp6_low,
                            'dhcp6_high': dhcp6_high
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
