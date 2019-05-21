
# batch name
def batchName(self, context):
    '''
        Button for the batch name operator.
    '''

    # row
    row = self.layout

    # operator; batch name
    row.operator('wm.batch_name', icon='SORTALPHA')
