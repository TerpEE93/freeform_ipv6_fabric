#
# parse_vrf_vlan.py
#   Version 0.2.0 - Initial Release
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
#

import pandas as pd
import json as j

vrf_vlan_dict = {}
vlans = {}
irb_prefix = ''
in_file = 'vrf_vlan.xls'
out_file = 'vrf_vlan.json'

df = pd.read_excel(in_file)

for row in list(range(len( df.index ))):
    s = df.iloc[ row ]
    if pd.notna( s[ 'VRF' ] ):
        tenant = s.loc[ 'VRF' ]
        index = int(s.loc[ 'vrf_index' ])
        tenant_vni = 9000 + index
        lo0_unit = index
        vrf_name = tenant
        vlans = {}
    elif pd.notna(s[ 'VLAN' ]):
        vlan_id = int( s[ 'vlan_id' ] )
        vxlan_vni = int( index * 10000 + vlan_id )
        if pd.notna( s[ 'irb_prefix' ] ):
            irb_prefix = s[ 'irb_prefix' ]
        else:
            irb_prefix = ''
        vlans = { **vlans,
                      **{ s[ 'VLAN' ]:{ 'vlan_id':vlan_id,
                                        'vxlan_vni':vxlan_vni,
                                        'irb_prefix':irb_prefix } } }
        vrf_vlan_dict.update( { tenant:{ 'vrf_name':tenant,
                                         'tenant_vni':tenant_vni,
                                         'lo0_unit':index,
                                         'vlans':vlans} } )

with open( out_file, 'w' ) as f:
    f.write(j.dumps( vrf_vlan_dict, indent=4 ))
    f.close
