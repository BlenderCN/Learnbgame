
def toggle(self, context):

    if context.space_data.viewport_shade == 'SOLID' or context.scene.silhouette.show_silhouette:

        layout = self.layout

        layout.prop(context.scene.silhouette, 'show_silhouette')

        if context.scene.silhouette.show_silhouette:

            layout.prop(context.user_preferences.themes['Default'].view_3d.space.gradients, 'high_gradient', text='')
