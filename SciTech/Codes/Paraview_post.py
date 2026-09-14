# trace generated using paraview version 6.2.0-RC1
#import paraview
#paraview.compatibility.major = 6
#paraview.compatibility.minor = 2


#### import the simple module from the paraview
from paraview.simple import *

# =================================================================================================================
# IMPORTANT NOTE:
"""
To execute this function, please run this file as follows:
excute on terminal btw:
path/ pvpython Paraview_post.py
"""
# =================================================================================================================

def paraview_postprocessing(input_file_name, output_file_name):
    #### disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()

    # create a new 'XML Unstructured Grid Reader'
    surface_flowvtu = XMLUnstructuredGridReader(registrationName='surface_flow.vtu', FileName=[input_file_name])

    # Properties modified on surface_flowvtu
    surface_flowvtu.Set(
        PointArrayStatus=['Pressure_Coefficient'],
        TimeArray='None',
    )

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')

    # show data in view
    surface_flowvtuDisplay = Show(surface_flowvtu, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    surface_flowvtuDisplay.Representation = 'Surface'

    # reset view to fit data
    renderView1.ResetCamera(False, 0.9)

    #changing interaction mode based on data extents
    renderView1.Set(
        InteractionMode='2D',
        CameraPosition=[1.5, 0.05000000074505806, 10.05],
        CameraFocalPoint=[1.5, 0.05000000074505806, 0.0],
    )

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # change representation type
    surface_flowvtuDisplay.SetRepresentationType('Wireframe')

    # get layout
    layout1 = GetLayout()

    # split cell
    layout1.SplitHorizontal(0, 0.5)

    # set active view
    SetActiveView(None)

    # Create a new 'SpreadSheet View'
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.Set(
        ColumnToSort='',
        BlockSize=1024,
    )

    # show data in view
    surface_flowvtuDisplay_1 = Show(surface_flowvtu, spreadSheetView1, 'SpreadSheetRepresentation')

    # assign view to a particular cell in the layout
    AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=2)

    # export view
    ExportView(output_file_name, view=spreadSheetView1, FrameWindow=[0, 0])

    #================================================================
    # addendum: following script captures some of the application
    # state to faithfully reproduce the visualization during playback
    #================================================================

    #--------------------------------
    # saving layout sizes for layouts

    # layout/tab size in pixels
    layout1.SetSize(899, 400)

    #-----------------------------------
    # saving camera placements for views

    # current camera placement for renderView1
    renderView1.Set(
        InteractionMode='2D',
        CameraPosition=[1.5, 0.05000000074505806, 10.05],
        CameraFocalPoint=[1.5, 0.05000000074505806, 0.0],
        CameraParallelScale=1.5008331020051848,
    )

    return output_file_name
    ##--------------------------------------------
    ## You may need to add some code at the end of this python script depending on your usage, eg:
    #
    ## Render all views to see them appears
    # RenderAllViews()
    #
    ## Interact with the view, usefull when running from pvpython
    # Interact()
    #
    ## Save a screenshot of the active view
    # SaveScreenshot("path/to/screenshot.png")
    #
    ## Save a screenshot of a layout (multiple splitted view)
    # SaveScreenshot("path/to/screenshot.png", GetLayout())
    #
    ## Save all "Extractors" from the pipeline browser
    # SaveExtracts()
    #
    ## Save a animation of the current active view
    # SaveAnimation()
    #
    ## Please refer to the documentation of paraview.simple
    ## https://www.paraview.org/paraview-docs/nightly/python/
    ##--------------------------------------------




import sys

if len(sys.argv) != 3:
    print("Uso: pvpython Paraview_post.py <input_file> <output_file>")
    sys.exit(1)

input_file_name = sys.argv[1]
output_file_name = sys.argv[2]

paraview_postprocessing(input_file_name, output_file_name)