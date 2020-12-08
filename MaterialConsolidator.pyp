import c4d
from c4d import gui, documents, plugins

class MaterialConsolidator(plugins.CommandData):
    def Execute(self, doc):
        objs = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
    
        if objs.__len__() == 0:
            gui.MessageDialog("No Objects Selected.")
            return

        for o in objs:
            MaterialDict = {}
            KeyDict = {}
            KeyIndexIt = 0
            SelectionDict = {}

            # Fill out MaterialDict
            tags = o.GetTags()
            for t in tags:
                if t.GetType() == c4d.Tpolygonselection:
                    SelectionDict[t.GetName()] = t

                if t.GetType() == c4d.Ttexture:
                    mat = t.GetMaterial()
                    KeyIndex = -1

                    for i in KeyDict:
                        if KeyDict[i] == mat:
                            KeyIndex = i
                            break
                        
                    if KeyIndex == -1:
                        KeyIndex = KeyIndexIt
                        KeyIndexIt += 1
                        KeyDict[KeyIndex] = mat

                    if KeyIndex not in MaterialDict:
                        MaterialDict[KeyIndex] = {"SelectionTags" : [], "MaterialTags" : []}

                    MaterialDict[KeyIndex]["MaterialTags"].append(t)
                    MaterialDict[KeyIndex]["SelectionTags"].append(t[c4d.TEXTURETAG_RESTRICTION])

            # Perform the selection merging
            for matIndex in MaterialDict:
                # consolidate the selection tags               
                selectionTags = MaterialDict[matIndex]["SelectionTags"]
                TagName = selectionTags[0]
                firstBS = SelectionDict[TagName].GetBaseSelect()      

                for tagIndex in range(1,selectionTags.__len__()):
                    secondBS = SelectionDict[selectionTags[tagIndex]].GetBaseSelect()
                    firstBS.Merge(secondBS)
                    SelectionDict[selectionTags[tagIndex]].Remove()
                    TagName += ";" + selectionTags[tagIndex]

                SelectionDict[selectionTags[0]].SetName(TagName)

                # consolidate the material tags
                materialTags = MaterialDict[matIndex]["MaterialTags"]
                materialTags[0][c4d.TEXTURETAG_RESTRICTION] = TagName
                for tagIndex in range(1,materialTags.__len__()):
                    materialTags[tagIndex].Remove()
            
    def GetScriptName(self):
        return "Material Consolidator"

def main():
    plugins.RegisterCommandPlugin(id=1056302, str="Material Consolidator", info=0, icon=None, help="Consolidates polygon selection tags by merging them when they share a material.", dat=MaterialConsolidator())

if __name__=='__main__':
    main()