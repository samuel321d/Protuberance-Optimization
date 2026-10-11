from paraview.simple import *
import sys

def paraview_postprocessing(input_file_name, output_file_name,  integral_file_name, x_min, xmax):
    """
    Function that executes a paraview script to obtain pressure coefficient distributions on the surface of the rocket and the integral of the pressure coefficient over the surface.
    Inputs:
    input_file_name: Name of the input VTU file
    output_file_name: Name of the output file for the pressure coefficient distributions
    integral_file_name: Name of the output file for the integral of the pressure coefficient
    x_min: Minimum x-coordinate for the clipping region
    xmax: Maximum x-coordinate for the clipping region

    """

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

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # change representation type
    surface_flowvtuDisplay.SetRepresentationType('Wireframe')

    # create a new 'Clip'
    clip1 = Clip(registrationName='Clip1', Input=surface_flowvtu)

    # Properties modified on clip1.ClipType
    clip1.ClipType.Normal = [0.0, 1.0, 0.0]

    # show data in view
    clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip1Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(surface_flowvtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip1.ClipType)

    # create a new 'Clip'
    clip2 = Clip(registrationName='Clip2', Input=surface_flowvtu)

    # Properties modified on clip2.ClipType
    clip2.ClipType.Origin = [x_max, 0, 0.0]

    # show data in view
    clip2Display = Show(clip2, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip2Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(clip1)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip2.ClipType)

    # toggle interactive widget visibility (only when running from the GUI)
    ShowInteractiveWidgets(proxy=clip1.ClipType)

    # set active source
    SetActiveSource(surface_flowvtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip1.ClipType)

    # set active source
    SetActiveSource(clip2)

    # toggle interactive widget visibility (only when running from the GUI)
    ShowInteractiveWidgets(proxy=clip2.ClipType)

    # Properties modified on clip2.ClipType
    clip2.ClipType.Normal = [-1.0, 0.0, 0.0]

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(surface_flowvtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip2.ClipType)

    # create a new 'Clip'
    clip3 = Clip(registrationName='Clip3', Input=surface_flowvtu)

    # Properties modified on clip3.ClipType
    clip3.ClipType.Origin = [x_min, 0, 0.0]

    # show data in view
    clip3Display = Show(clip3, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip3Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(surface_flowvtu)

    # toggle interactive widget visibility (only when running from the GUI)
    HideInteractiveWidgets(proxy=clip3.ClipType)

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

    # destroy spreadSheetView1
    Delete(spreadSheetView1)
    del spreadSheetView1

    # close an empty frame
    layout1.Collapse(2)

    # set active view
    SetActiveView(renderView1)

    # create a new 'Integrate Variables'
    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=surface_flowvtu)

    # set active source
    SetActiveSource(surface_flowvtu)

    # set active source
    SetActiveSource(integrateVariables1)

    # set active source
    SetActiveSource(surface_flowvtu)

    # destroy integrateVariables1
    Delete(integrateVariables1)
    del integrateVariables1

    # get animation scene
    animationScene1 = GetAnimationScene()

    # update animation scene based on data timesteps
    animationScene1.UpdateAnimationUsingDataTimeSteps()

    # create a new 'Integrate Variables'
    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=surface_flowvtu)

    # Create a new 'SpreadSheet View'
    spreadSheetView1 = CreateView('SpreadSheetView')
    spreadSheetView1.Set(
        ColumnToSort='',
        BlockSize=1024,
    )

    # show data in view
    integrateVariables1Display = Show(integrateVariables1, spreadSheetView1, 'SpreadSheetRepresentation')

    # add view to a layout so it's visible in UI
    AssignViewToLayout(view=spreadSheetView1, layout=layout1, hint=0)

    # update the view to ensure updated data information
    renderView1.Update()

    # update the view to ensure updated data information
    spreadSheetView1.Update()

    # export view
    ExportView(integral_file_name, view=spreadSheetView1, FrameWindow=[0, 0])
            
    return output_file_name, integral_file_name

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: pvpython Paraview_post.py <input_file> <output_file> <integral_file>")
        sys.exit(1)
    out, integ = paraview_postprocessing(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Archivo generado:", out)