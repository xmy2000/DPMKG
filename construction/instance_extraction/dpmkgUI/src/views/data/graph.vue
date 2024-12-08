<template>
  <el-form :inline="true" :model="formInline">
    <el-form-item label="Domain">
      <el-input v-model="formInline.domain" placeholder="Domain" clearable />
    </el-form-item>
    <el-form-item label="Relationship">
      <el-select
        v-model="formInline.relationship"
        placeholder="Relationship"
        clearable
      >
        <el-option label="Zone one" value="shanghai" />
        <el-option label="Zone two" value="beijing" />
      </el-select>
    </el-form-item>
    <el-form-item label="Target">
      <el-input v-model="formInline.target" placeholder="Target" clearable />
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onSubmit">Query</el-button>
    </el-form-item>
  </el-form>
  <div>
    <div style="height:calc(100vh - 160px);">
      <RelationGraph
        ref="graphRef"
        :options="graphOptions"
        :on-node-click="onNodeClick"
        :on-line-click="onLineClick"
      />
    </div>
  </div>

  <el-dialog v-model="dialogFormVisible" title="Node Property" width="30%">
    <el-form
      label-position="right"
      label-width="100px"
      style="max-width: 460px"
    >
      <el-form-item
        v-for="(value, key) in nodeProperty"
        :key="key"
        :label="key"
      >
        <el-input v-model="nodeProperty[key]" />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogFormVisible = false">
          Confirm
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import RelationGraph from 'relation-graph/vue3'
import { List, GetNodeProperty } from '@/api/graph'
export default {
  name: 'Graph',
  components: { RelationGraph },
  data() {
    return {
      formInline: '',
      graphData: '',
      nodeProperty: '',
      dialogFormVisible: false,
      graphOptions: {
        moveToCenterWhenRefresh: false,
        zoomToFitWhenRefresh: false,
        useAnimationWhenRefresh: true,
        defaultFocusRootNode: false,
        backgrounImageNoRepeat: true,
        defaultExpandHolderPosition: 'top',
        defaultNodeBorderWidth: 5,
        defaultLineWidth: 3,
        defaultLineShape: 5,
        defaultLineMarker: {
          markerWidth: 12,
          markerHeight: 12,
          refX: 6,
          refY: 6,
          data: 'M2,2 L10,6 L2,10 L6,6 L2,2',
        },
        layouts: [
          {
            label: '中心',
            layoutName: 'force',
            maxLayoutTimes: 100,
            force_node_repulsion: 0.5,
            force_line_elastic: 2.5,
          },
        ],
      },
    }
  },
  mounted() {
    this.showGraph()
  },
  methods: {
    async showGraph() {
      this.graphData = await List()
      console.log(this.graphData)
      this.$refs.graphRef.setJsonData(this.graphData, graphInstance => {
        // Called when the relation-graph is completed
      })
    },
    async onNodeClick(nodeObject, $event) {
      console.log('onNodeClick:', nodeObject)
      this.nodeProperty = await GetNodeProperty({ id: nodeObject.id })
      console.log('nodeProperty:', this.nodeProperty)

      this.dialogFormVisible = true
    },
    onLineClick(lineObject, $event) {
      console.log('onLineClick:', lineObject)
    },
  },
}
</script>
