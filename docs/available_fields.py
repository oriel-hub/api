#!/usr/bin/python

import unicodecsv

with open('available_fields.csv', 'rb') as f:
    reader = unicodecsv.reader(f)
    header_row = reader.next()
    
    assert header_row[0] == 'Field name'
    assert header_row[11] == 'Description'
    
    with open('available_fields.rst', 'w') as out:
        for i, row in enumerate(reader):
            if len(row) >= 12:
                name = row[0]
                if len(name) == 0:
                    print "Ignoring row %d with no field name" % (i + 2)
                else:
                    out.write(name + '\n')
                    desc = row[11]
                    if len(desc) == 0:
                        desc = "No description"
                    out.write('  ' + desc + '\n\n')
            else:
                print "Ignoring row %d with %d columns" % (i + 2, len(row))
        
 
 