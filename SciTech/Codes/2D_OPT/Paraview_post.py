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
    #==================================================================================
    # Initial set up and vtu file import
    #==================================================================================
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
    #==================================================================================
    
    #==================================================================================
    #Clip functions to limit hermite region
    #==================================================================================

    # 3 main clips are described here
    # Clips are defined by an ORIGIN point and a NORMAL vector.
    # create a new 'Clip'
    clip1 = Clip(registrationName='Clip1', Input=surface_flowvtu)

    # Properties modified on clip1.ClipType
    #clip1.ClipType.Normal = [0.0, -1.0, 0.0]
    clip1.ClipType.Set(
        Origin=[0.0, 1.0, 0.0],
        Normal=[-1.0, 0.0, 0.0],
    )

    # show data in view
    clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip1Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(surfacevtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip1.ClipType)

    # create a new 'Clip'
    clip2 = Clip(registrationName='Clip2', Input=surface_flowvtu)

    # Properties modified on clip2.ClipType
    #clip2.ClipType.Origin = [0.0, 1.0, 0.0]
    clip2.ClipType.Set(
    Origin=[0.0, 1.0, 0.0],
    Normal=[1.0, 0.0, 0.0],
    )
    # show data in view
    clip2Display = Show(clip2, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip2Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(surfacevtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip2.ClipType)

    # create a new 'Clip'
    clip3 = Clip(registrationName='Clip3', Input=surface_flowvtu)

    # Properties modified on clip3.ClipType
    clip3.ClipType.Set(
        Origin=[3.0, 0.0, 0.0],
        Normal=[-1.0, 0.0, 0.0],
    )

    # show data in view
    clip3Display = Show(clip3, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip3Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()
    #==================================================================================
    # Integrate Cp over protuberance
    #==================================================================================
    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=clip3)

    #==================================================================================
    # Cp distriution export in CSV format
    #==================================================================================
        

    # find source
    clip3 = FindSource('Clip3')

    # set active source
    SetActiveSource(clip3)

    # toggle interactive widget visibility (only when running from the GUI)
    ShowInteractiveWidgets(proxy=clip3.ClipType)

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')

    # get display properties
    clip3Display = GetRepresentation(clip3, view=renderView1)

    # get layout
    layout1 = GetLayout()

    # split cell
    layout1.SplitHorizontal(1, 0.5)

    # set active view
    SetActiveView(None)

    # Create a new 'SpreadSheet View'
    spreadSheetView2 = CreateView('SpreadSheetView')
    spreadSheetView2.Set(
        ColumnToSort='',
        BlockSize=1024,
    )

    # show data in view
    clip3Display_1 = Show(clip3, spreadSheetView2, 'SpreadSheetRepresentation')

    # assign view to a particular cell in the layout
    AssignViewToLayout(view=spreadSheetView2, layout=layout1, hint=4)




    # export view
    ExportView(output_file_name, view=spreadSheetView2, FrameWindow=[0, 0])

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

    return output_file_name, integrateVariables1
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