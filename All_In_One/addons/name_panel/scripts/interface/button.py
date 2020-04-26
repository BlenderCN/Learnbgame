
# batch name
def batchName(self, context):
    '''
        Button for the batch name operator.
    '''

    # row
    row = self.layout

    # operator; batch name
    op = row.operator('wm.batch_name', icon='SORTALPHA')
    op.simple = False
    op.quickBatch = False
