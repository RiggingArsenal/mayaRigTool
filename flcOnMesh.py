import maya.cmds as cmds


def uvOnSel(sel):
    cmds.select(sel)
    # Query uv
    cmds.ConvertSelectionToUVs()
    uvValues = cmds.polyEditUV(query=True)
    cmds.ConvertSelectionToVertices()
    cmds.select(cl=True)
    return uvValues


def flcOnMesh():
    sel = cmds.ls(sl=True, fl=True) or []
    cmds.select(cl=True)

    if sel:
        flcList = []

        for i in range(0, len(sel)):
            objName = sel[i].split('.')[0]
            objShape = cmds.listRelatives(objName)[0]

            # Get the uv value
            uvValue = uvOnSel(sel[i])

            # create follicle
            flc = cmds.createNode('transform', n='{0}_{1}_{2}'.format('flc', objName, str(i+1).zfill(3)), ss=True)
            flcList.append(flc)
            flcShape = cmds.createNode('follicle', n='{}Shape'.format(flc), p=flc, ss=True)

            # connect follicleShape result to  follicle transform
            cmds.connectAttr('{}.outTranslate'.format(flcShape), '{}.translate'.format(flc), f=1)
            cmds.connectAttr('{}.outRotate'.format(flcShape), '{}.rotate'.format(flc), f=1)

            # Connect Shape out Mesh
            cmds.connectAttr('{}.worldMatrix[0]'.format(objShape), '{}.inputWorldMatrix'.format(flcShape), f=1)
            cmds.connectAttr('{}.outMesh'.format(objShape), '{}.inputMesh'.format(flcShape), f=1)

            cmds.setAttr("{}.parameterU".format(flcShape), uvValue[0])
            cmds.setAttr("{}.parameterV".format(flcShape), uvValue[1])

        # Organize follicles
        if not cmds.objExists('grp_flc'):
            flcGrp = cmds.group(name='grp_flc', empty=True)
            cmds.select(cl=True)
        else:
            flcGrp = 'grp_flc'

        cmds.parent(flcList, flcGrp)
        cmds.select(cl=True)


flcOnMesh()
