from paraview.simple import *
import sys

print("Iniciando Paraview_post.py", flush=True)
print("Argumentos:", sys.argv, flush=True)
def paraview_postprocessing(input_file_name, output_file_name,  integral_file_name, x_min, x_max):
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

    #changing interaction mode based on data extents
    renderView1.Set(
        CameraPosition=[1620.3255040943623, 10.499984741210938, 10851.819122567773],
        CameraFocalPoint=[1620.3255040943623, 10.499984741210938, 0.0],
    )

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # change representation type
    surface_flowvtuDisplay.SetRepresentationType('Wireframe')

    # create a new 'Clip'
    clip1 = Clip(registrationName='Clip1', Input=surface_flowvtu)

    # Properties modified on clip1
    clip1.Invert = 0

    # Properties modified on clip1.ClipType
    clip1.ClipType.Normal = [0.0, 1.0, 0.0]

    # show data in view
    clip1Display = Show(clip1, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip1Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # change representation type
    clip1Display.SetRepresentationType('Wireframe')

    # hide data in view
    Hide(surface_flowvtu, renderView1)

    # create a new 'Clip'
    clip2 = Clip(registrationName='Clip2', Input=clip1)

    # Properties modified on clip2
    clip2.Invert = 0

    # Properties modified on clip2.ClipType
    clip2.ClipType.Origin = [x_min, 59.24998474121094, 0.0]

    # show data in view
    clip2Display = Show(clip2, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip2Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # hide data in view
    Hide(clip1, renderView1)

    # change representation type
    clip2Display.SetRepresentationType('Wireframe')

    # create a new 'Clip'
    clip3 = Clip(registrationName='Clip3', Input=clip2)

    # Properties modified on clip3
    clip3.Invert = 0

    # Properties modified on clip3.ClipType
    clip3.ClipType.Set(
        Origin=[x_max, 59.24998474121094, 0.0],
        Normal=[-1.0, 0.0, 0.0],
    )

    # show data in view
    clip3Display = Show(clip3, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    clip3Display.Representation = 'Surface'

    # update the view to ensure updated data information
    renderView1.Update()

    # hide data in view
    Hide(clip2, renderView1)

    # change representation type
    clip3Display.SetRepresentationType('Wireframe')

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
    clip3Display_1 = Show(clip3, spreadSheetView1, 'SpreadSheetRepresentation')

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
    integrateVariables1 = IntegrateVariables(registrationName='IntegrateVariables1', Input=clip3)

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
    print("Archivo generado")        
    return output_file_name, integral_file_name


if __name__ == "__main__":
    print("Iniciando Paraview_post.py", flush=True)
    print("Argumentos:", sys.argv, flush=True)

    if len(sys.argv) != 6:
        print(f"Error: se esperaban 5 argumentos, recibidos {len(sys.argv)-1}", flush=True)
        sys.exit(1)

    try:
        print("Ejecutando postprocesamiento...", flush=True)

        out, integ = paraview_postprocessing(
            sys.argv[1],
            sys.argv[2],
            sys.argv[3],
            float(sys.argv[4]),
            float(sys.argv[5])
        )

        print("Archivo generado:", out, flush=True)
        print("Integral generada:", integ, flush=True)

    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
