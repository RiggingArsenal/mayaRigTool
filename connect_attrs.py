import pymel.core as pm


def shorten_attr(attr):
    if attr == 'translate' or attr == 'T':
        return 't'
    if attr == 'translateX':
        return 'tx'
    if attr == 'translateY':
        return 'ty'
    if attr == 'translateZ':
        return 'tz'
    if attr == 'rotate' or attr == 'R':
        return 'r'
    if attr == 'rotateX':
        return 'rx'
    if attr == 'rotateY':
        return 'ry'
    if attr == 'rotateZ':
        return 'rz'
    if attr == 'scale' or attr == 'S':
        return 's'
    if attr == 'scaleX':
        return 'sx'
    if attr == 'scaleY':
        return 'sy'
    if attr == 'scaleZ':
        return 'sz'
    if attr == 'visibility':
        return 'v'
    return attr


def get_plug(obj, attr):
    # Query the plugs
    plug = pm.listConnections(obj + '.' + attr, plugs=True) or []

    if plug:
        plug_name = plug[0].split('.')[0]
        plug_attr = plug[0].split('.')[-1]
        plug_attr = shorten_attr(plug_attr)

        # If plug equal unitConversion, find unitConversion's plug
        if 'unitConversion' in plug_name:
            plug = pm.listConnections(plug_name + '.input', plugs=True) or []
            if plug:
                plug_name = plug[0].split('.')[0]
                plug_attr = plug[0].split('.')[-1]
                plug_attr = shorten_attr(plug_attr)
                return plug_name, plug_attr
        else:
            return plug_name, plug_attr

    # Not plug, return plug_name False, plug_attr False
    else:
        return False, False


def disconnect(obj, attr):
    # If connect['t'], but ['tx', 'ty', 'tz'] already connected, disconnect ['tx', 'ty', 'tz']
    if attr in ['t', 'r', 's']:
        for attr_suffix in ['x', 'y', 'z']:
            plug = pm.listConnections(obj + '.' + attr + attr_suffix, plugs=True) or []

            if plug:
                plug_name = plug[0].split('.')[0]
                plug_attr = plug[0].split('.')[-1]
                plug_attr = shorten_attr(plug_attr)
                if plug_attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                    pm.disconnectAttr((plug_name + '.' + plug_attr), (obj + '.' + plug_attr))

    # If connect['tx'], but ['t'] already connected, disconnect ['t']
    if attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
        plug = pm.listConnections(obj + '.' + attr[:-1], plugs=True) or []

        if plug:
            plug_name = plug[0].split('.')[0]
            plug_attr = plug[0].split('.')[-1]
            plug_attr = shorten_attr(plug_attr)
            pm.disconnectAttr((plug_name + '.' + plug_attr), (obj + '.' + attr[:-1]))


def add_offset_node(A, B, attr, plug_name=None, plug_attr=None):
    attr = shorten_attr(attr)
    offset_PMA = None
    offset_MD = None

    # If connect['t'], but ['tx', 'ty', 'tz'] already connected, disconnect ['tx', 'ty', 'tz']
    # If connect['tx'], but ['t'] already connected, disconnect ['t']
    disconnect(B, attr)

    # Use multiplyDivide node as offset node for Scale
    # If attr == 's', 'sx', 'sy', 'sz', use the multiplyDivide node as offset node
    if attr in ['s', 'sx', 'sy', 'sz']:
        offset_MD = pm.shadingNode('multiplyDivide', asUtility=1)
        offset_MD = pm.rename(offset_MD, (B + "_Offset_" + pm.mel.capitalizeString(str(attr)) + '_MD'))

    # Use plusMinusAverage for normal offset node (e.g. Translate, Rotate, Visibility...)
    else:
        offset_PMA = pm.shadingNode('plusMinusAverage', asUtility=1)
        offset_PMA = pm.rename(offset_PMA, (B + "_Offset_" + pm.mel.capitalizeString(str(attr)) + '_PMA'))

    # ====================================================================================================
    # With Plug connect Mode
    # ====================================================================================================
    if plug_name and plug_attr:
        if offset_PMA:
            if attr in ['t', 'r']:
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input3D[0]'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_PMA + '.input3D[1]'), f=1)
                pm.connectAttr((offset_PMA + '.output3D'), (B + '.' + attr), f=1)
            else:
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input1D[0]'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_PMA + '.input1D[1]'), f=1)
                pm.connectAttr((offset_PMA + '.output1D'), (B + '.' + attr), f=1)

        if offset_MD:
            if attr in ['s']:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_MD + '.input2'), f=1)
                pm.connectAttr((offset_MD + '.output'), (B + '.' + attr), f=1)
            else:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1X'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_MD + '.input2X'), f=1)
                pm.connectAttr((offset_MD + '.outputX'), (B + '.' + attr), f=1)

    # ====================================================================================================
    # Normal connect Mode
    # ====================================================================================================
    else:
        if offset_PMA:
            if attr in ['t', 'r']:
                ori_attr_x_val = pm.getAttr(B + '.%sx' % attr)
                ori_attr_y_val = pm.getAttr(B + '.%sy' % attr)
                ori_attr_z_val = pm.getAttr(B + '.%sz' % attr)
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input3D[0]'), f=1)
                pm.mel.AEnewNonNumericMultiAddNewItem(offset_PMA, "input3D[1]")
                pm.setAttr(offset_PMA + ".input3D[1].input3Dx", ori_attr_x_val)
                pm.setAttr(offset_PMA + ".input3D[1].input3Dy", ori_attr_y_val)
                pm.setAttr(offset_PMA + ".input3D[1].input3Dz", ori_attr_z_val)
                pm.connectAttr((offset_PMA + '.output3D'), (B + '.' + attr), f=1)

            else:
                ori_attr_val = pm.getAttr(B + '.' + attr)
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input1D[0]'), f=1)
                pm.mel.AEnewNonNumericMultiAddNewItem(offset_PMA, "input2D")
                pm.setAttr(offset_PMA + ".input1D[1]", ori_attr_val)
                pm.connectAttr((offset_PMA + '.output1D'), (B + '.' + attr), f=1)

        if offset_MD:
            if attr in ['s']:
                ori_attr_x_val = pm.getAttr(B + '.%sx' % attr)
                ori_attr_y_val = pm.getAttr(B + '.%sy' % attr)
                ori_attr_z_val = pm.getAttr(B + '.%sz' % attr)
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1'), f=1)
                pm.setAttr(offset_MD + ".input2X", ori_attr_x_val)
                pm.setAttr(offset_MD + ".input2Y", ori_attr_y_val)
                pm.setAttr(offset_MD + ".input2Z", ori_attr_z_val)
                pm.connectAttr((offset_MD + '.output'), (B + '.' + attr), f=1)

            else:
                ori_attr_val = pm.getAttr(B + '.' + attr)
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1X'), f=1)
                pm.setAttr(offset_MD + ".input2X", ori_attr_val)
                pm.connectAttr((offset_MD + '.outputX'), (B + '.' + attr), f=1)


def add_specify_offset_node(A, B, attr, plug_name=None, plug_attr=None, specify_node=None):
    attr = shorten_attr(attr)
    offset_PMA = None
    offset_MD = None

    # If connect['t'], but ['tx', 'ty', 'tz'] already connected, disconnect ['tx', 'ty', 'tz']
    # If connect['tx'], but ['t'] already connected, disconnect ['t']
    disconnect(B, attr)

    # Use multiplyDivide node as offset node for Scale
    # If attr == 's', 'sx', 'sy', 'sz', use the multiplyDivide node as offset node
    if specify_node == 'multiplyDivide' or specify_node == 'MD':
        offset_MD = pm.shadingNode('multiplyDivide', asUtility=1)
        offset_MD = pm.rename(offset_MD, (B + "_Offset_" + pm.mel.capitalizeString(str(attr)) + '_MD'))

    # Use plusMinusAverage for normal offset node (e.g. Translate, Rotate, Visibility...)
    if specify_node == 'plusMinusAverage' or specify_node == 'PMA':
        offset_PMA = pm.shadingNode('plusMinusAverage', asUtility=1)
        offset_PMA = pm.rename(offset_PMA, (B + "_Offset_" + pm.mel.capitalizeString(str(attr)) + '_PMA'))

    # ====================================================================================================
    # With Plug connect Mode
    # ====================================================================================================
    # If plug.attr == A.attr, switch normal connect mode
    if plug_name and plug_attr:
        if (plug_name + '.' + plug_attr) == (A + '.' + attr):
            plug_name = None
            plug_attr = None

    if plug_name and plug_attr:
        if offset_PMA:
            if attr in ['t', 'r', 's']:
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input3D[0]'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_PMA + '.input3D[1]'), f=1)
                pm.connectAttr((offset_PMA + '.output3D'), (B + '.' + attr), f=1)
            else:
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input1D[0]'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_PMA + '.input1D[1]'), f=1)
                pm.connectAttr((offset_PMA + '.output1D'), (B + '.' + attr), f=1)

        if offset_MD:
            if attr in ['t', 'r', 's']:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_MD + '.input2'), f=1)
                pm.connectAttr((offset_MD + '.output'), (B + '.' + attr), f=1)
            else:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1X'), f=1)
                pm.connectAttr((plug_name + '.' + plug_attr), (offset_MD + '.input2X'), f=1)
                pm.connectAttr((offset_MD + '.outputX'), (B + '.' + attr), f=1)

    # ====================================================================================================
    # Normal connect Mode
    # ====================================================================================================
    else:
        if offset_PMA:
            if attr in ['t', 'r', 's']:
                ori_attr_x_val = pm.getAttr(B + '.%sx' % attr)
                ori_attr_y_val = pm.getAttr(B + '.%sy' % attr)
                ori_attr_z_val = pm.getAttr(B + '.%sz' % attr)
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input3D[0]'), f=1)
                pm.mel.AEnewNonNumericMultiAddNewItem(offset_PMA, "input3D[1]")
                pm.setAttr(offset_PMA + ".input3D[1].input3Dx", ori_attr_x_val)
                pm.setAttr(offset_PMA + ".input3D[1].input3Dy", ori_attr_y_val)
                pm.setAttr(offset_PMA + ".input3D[1].input3Dz", ori_attr_z_val)
                pm.connectAttr((offset_PMA + '.output3D'), (B + '.' + attr), f=1)

            else:
                ori_attr_val = pm.getAttr(B + '.' + attr)
                pm.connectAttr((A + '.' + attr), (offset_PMA + '.input1D[0]'), f=1)
                pm.mel.AEnewNonNumericMultiAddNewItem(offset_PMA, "input2D")
                pm.setAttr(offset_PMA + ".input1D[1]", ori_attr_val)
                pm.connectAttr((offset_PMA + '.output1D'), (B + '.' + attr), f=1)

        if offset_MD:
            if attr in ['t', 'r', 's']:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1'), f=1)
                pm.connectAttr((offset_MD + '.output'), (B + '.' + attr), f=1)

            else:
                pm.connectAttr((A + '.' + attr), (offset_MD + '.input1X'), f=1)
                pm.connectAttr((offset_MD + '.outputX'), (B + '.' + attr), f=1)


def connect_attrs(attrs=[], offset_node=True, specify_node=False):
    sel = pm.ls(sl=True)

    # Check user selection
    run = True

    if sel:
        if len(sel) < 2:
            run = False
    else:
        run = False

    # If the user selects the first target A and target B...
    if run:
        # Store first selection
        first_sel = sel[0]

        # Remove the first select from the sel
        sel = sel[1:]

        for each in sel:
            if not attrs:
                # If there is no attrs input, will use this default attrs
                attrs = ['t', 'r']

            for attr in attrs:
                attr = shorten_attr(attr)

                # Get each.attr plug
                plug_name, plug_attr = get_plug(each, attr)

                # If each.attr plug exist
                if plug_name:
                    # Add offset node for connection
                    if specify_node:
                        add_specify_offset_node(first_sel, each, attr, plug_name, plug_attr, specify_node=specify_node)
                    else:
                        add_offset_node(first_sel, each, attr, plug_name, plug_attr)

                else:
                    # Toggle add offset node mode
                    if offset_node:
                        # Add offset node for connection, offset node will keep the B's attr current value
                        if specify_node:
                            add_specify_offset_node(first_sel, each, attr, specify_node=specify_node)
                        else:
                            add_offset_node(first_sel, each, attr)

                    # Toggle directly connect mode
                    else:
                        # If connect['t'], but ['tx', 'ty', 'tz'] already connected, disconnect ['tx', 'ty', 'tz']
                        # If connect['tx'], but ['t'] already connected, disconnect ['t']
                        disconnect(each, attr)

                        # Just connect the attrs
                        pm.connectAttr((first_sel + '.' + attr), (each + '.' + attr), f=1)

        # Clear the selection
        pm.select(cl=True)

        # Re-select user's selection
        pm.select(first_sel, sel, r=True)

    else:
        pm.warning('Please select the first target A and target B...')


# User could provide the attrs,
# e.g. attrs=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']
# e.g. attrs=['t', 'r', 's',]
# The default attrs=['t', 'r']
connect_attrs(attrs=['t', 'r'], offset_node=True, specify_node=False)
