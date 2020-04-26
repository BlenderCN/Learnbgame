Node
----
OpenCV Laboratory is a series of pre-installed Python libraries and a set of Blender extensions. On this basis, a set of OpenCV functions has been implemented in the form of convenient to connect nodes where we have quick and convenient access to all function parameters and an immediate preview of the effects of these functions.

The node is represented by a rectangle with rounded corners in OpenCV Laboratory.
Each of them has a circular input socket(s) on the left and an output socket(s) on the opposite side.

The example with a brief description of different nodes is below:

.. image:: http://kube.pl/wp-content/uploads/2018/05/nodes_1-e1525848678402.png

1. Nodes name.
2. Input sockets.
3. Output socket.
4. Input parameters to which the corresponding input sockets are assigned. It is often possible to freely adjust individual arguments using the sliders or by entering a specific value.
5. The output parameter is the result of operations performed by the node.
6. An internal parameter that is a list for selecting a specific function.
7. Internal parameter in the form of buttons defining the selection of functions.
8. An internal parameter in the form of an acceptance field taking into account the function.
9. A button to minimize the view of the node.

Interconnecting of nodes
------------------------
Interconnecting nodes is nothing more than a command for a computer program to perform the relevant functions, specifying the final result of their actions. Interconnecting individual nodes is a relatively simple procedure consisting in connecting, by means of a line, the output socket of one of the nodes with the appropriate input socket of another one.

.. image:: http://kube.pl/wp-content/uploads/2018/05/connect-e1526797052886.png

A) First node
B) Second node
C) Output socket
D) Input socket
E) Interconnecting

The above operation is performed as follows:
    1. Left-click on the output socket of the node.
    2. Without releasing the button, route the lines to the input of another node.
    3. Release the mouse button.

No complex operations are applied in this example so resulting in an output image identical to the input image.

Incorrect input data of a node
------------------------------
Not all nodes can be directly connected to each other due to their properties and functions. Each node requires a specific parameter to be entered at the appropriate input, some of which require all relevant data to be entered. Any irregularities in the above cases are illustrated by a change in the color of the node.

.. image:: http://kube.pl/wp-content/uploads/2018/05/connect_wrong-e1526794915757.png

a) correct input data of the node
b) incorrect input data of the node
c) lack of necessary data at the input of the node

It is often enough to make a small correction to the node settings or to add the required data or to use a compilation of other nodes if necessary.