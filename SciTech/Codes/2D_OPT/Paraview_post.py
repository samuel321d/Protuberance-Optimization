from paraview.simple import *
import sys

def paraview_postprocessing(input_file_name, output_file_name,  integral_file_name):

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
        CameraPosition=[1589.2040729522705, -1.52587890625e-05, 10792.332711219788],
        CameraFocalPoint=[1589.2040729522705, -1.52587890625e-05, 0.0],
    )

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # create a new 'Clip'
    clip1 = Clip(registrationName='Clip1', Input=surface_flowvtu)

    # Properties modified on clip1.ClipType
    clip1.ClipType.Normal = [0.0, 1.0, 0.0]

    # show data in view
    clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip1Display.Representation = 'Surface'

    # hide data in view
    Hide(surface_flowvtu, renderView1)

    # update the view to ensure updated data information
    renderView1.Update()

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
    clip1Display_1 = Show(clip1, spreadSheetView1, 'SpreadSheetRepresentation')

    # assign view to a particular cell in the layout
    AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=2)

    # export view
    ExportView(output_file_name, view=spreadSheetView1, FrameWindow=[0, 0])

    # create a new 'Integrate Variables'
    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=clip1)

    # show data in view
    integrateVariables1Display = Show(integrateVariables1, spreadSheetView1, 'SpreadSheetRepresentation')

    # update the view to ensure updated data information
    renderView1.Update()

    # update the view to ensure updated data information
    spreadSheetView1.Update()

    # export view
    ExportView(integral_file_name, view=spreadSheetView1, FrameWindow=[0, 0])

    #================================================================
    # addendum: following script captures some of the application
    # state to faithfully reproduce the visualization during playback
    #================================================================

    #--------------------------------
    # saving layout sizes for layouts

    # layout/tab size in pixels
    layout1.SetSize(858, 476)

    #-----------------------------------
    # saving camera placements for views

    # current camera placement for renderView1
    renderView1.Set(
        InteractionMode='2D',
        CameraPosition=[1589.2040729522705, -1.52587890625e-05, 10792.332711219788],
        CameraFocalPoint=[1589.2040729522705, -1.52587890625e-05, 0.0],
        CameraParallelScale=1613.143675744214,
    )


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
        
    return output_file_name, integral_file_name

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: pvpython Paraview_post.py <input_file> <output_file> <integral_file>")
        sys.exit(1)
    out, integ = paraview_postprocessing(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Archivo generado:", out)