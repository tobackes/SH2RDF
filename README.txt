We are assuming the input data as column based input format.

As a row in a table-based dataset does not contain lists, each row constitutes a minimal piece of information.

We add a rowID column to the input data.

Here, each row contains information about one occupation_item for a certain person.

We define a preset structure for the output format and a context definition to map it to schema.org.

The preset structure only needs to hold the type information for objects/nodes.

For each column we define as a dictionary with empty fields, which information can be found in this column and where to put it in the overall structure, i.e.:

    {'smart_harvesting':{'':{'occupations':{'':{'institution_l2':{'@id':None,'location':None,'name':None}}}}}}

Then the parsing function determines how to find the values to fit into these fields.

The resulting instantiated object is 'added' onto the overall structure by means of a hierarchical update function merge().

For this reason, we do not use lists containing objects/nodes, but only for primitive datatypes like strings.

As each object needs an id value anyway, we can also use this as a key in the respective parent dictionary, but at first, the keys are instatiated as "", as the id is only known after parsing the row.

Once we have read a line, we replace the empty "" key in the current row's representation with the value in the respective @id field that was filled during parsing.

After each row, we insert the final keys and merge the structure for this row with the global final representation object under construction.

We repeat until all input rows are processed and merge the result with the context definition to obtain the JSON-LD output.
