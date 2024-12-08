<template>
  <el-row :gutter="10">
    <el-col :span="6">
      <el-input
        v-model="input"
        class="w-50 m-2"
        placeholder=""
        prefix-icon="Search"
      />
    </el-col>

    <el-button type="primary">Search</el-button>
    <el-button type="success">Upload SysML Model</el-button>
    <el-button type="warning" @click="preview">
      Preview Graph Database
    </el-button>
  </el-row>
  <br />
  <el-table :data="tableData" strip style="width: 100%" table-layout="auto">
    <el-table-column prop="index" label="Index" />
    <el-table-column prop="sysml" label="SysML Model" />
    <el-table-column prop="owl" label="OWL Model" />
    <!-- <el-table-column prop="user" label="User" /> -->

    <el-table-column label="User">
      <template #default="scope">
        <el-popover effect="light" trigger="hover" placement="top" width="auto">
          <template #reference>
            <el-tag>{{ scope.row.user }}</el-tag>
          </template>
        </el-popover>
      </template>
    </el-table-column>

    <el-table-column label="Date">
      <template #default="scope">
        <div style="display: flex; align-items: center">
          <el-icon><timer /></el-icon>
          <span style="margin-left: 10px">{{ scope.row.date }}</span>
        </div>
      </template>
    </el-table-column>

    <!-- <el-table-column prop="status" label="status" /> -->
    <el-table-column prop="status" label="status">
      <template #default="scope">
        <el-switch
          v-model="scope.row.status"
          size="large"
          active-text="Enable"
          inactive-text="Disable"
        />
      </template>
    </el-table-column>

    <el-table-column label="Operations">
      <template #default="scope">
        <el-button
          size="small"
          type="primary"
          round
          @click="dialogFormVisible2 = true"
        >
          Convert SysML to OWL
        </el-button>
        <el-button
          size="small"
          type="info"
          round
          @click="handleEdit(scope.$index, scope.row)"
        >
          Edit Ontology
        </el-button>
        <el-button
          size="small"
          type="warning"
          round
          @click="dialogFormVisible = true"
        >
          Extract Data
        </el-button>
        <el-button
          size="small"
          type="danger"
          round
          @click="handleDelete(scope.$index, scope.row)"
        >
          Delete Model
        </el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-dialog v-model="dialogFormVisible" title="Extract data">
    <el-form
      :model="form"
      label-position="top"
      size="large"
      style="max-width: 460px"
      label-width="auto"
    >
      <el-form-item label="Ontology name:">
        <el-input v-model="form.name" autocomplete="off" style="width: 240px" />
      </el-form-item>
      <el-form-item label="Data source:">
        <el-select
          v-model="form.datasource"
          multiple
          placeholder="Select"
          style="width: 240px"
        >
          <el-option
            v-for="item in options"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <el-text>Progress:</el-text>
    <el-progress
      :percentage="100"
      :stroke-width="15"
      status="success"
      striped
      striped-flow
      :duration="10"
    />
    <el-divider />
    <el-text class="mx-1" type="success">
      Data extraction done!
    </el-text>
    <br />
    <el-text>Number of added graph nodes: 10</el-text>
    <br />
    <el-text>Number of associations added: 20</el-text>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
        <el-button type="primary" @click="dialogFormVisible = false">
          Confirm
        </el-button>
      </span>
    </template>
  </el-dialog>

  <el-dialog v-model="dialogFormVisible2" title="Convert SysML" width="100%">
    <el-text>Progress:</el-text>
    <el-progress
      :percentage="100"
      :stroke-width="15"
      status="success"
      striped
      striped-flow
      :duration="10"
    />
    <el-text class="mx-1" type="success">
      SysML model convert done!
    </el-text>
    <el-divider />
    <el-descriptions title="Convert Info" size="large" border>
      <el-descriptions-item label="SysML Model Summary">
        解析package: 38; 解析block: 130; 解析association: 84; 解析dataType: 8;
        解析activity: 16; 解析关联关系: 294
      </el-descriptions-item>
      <el-descriptions-item label="Ontology Model Summary">
        生成class: 752; 生成objectProperty: 17; 生成datatypeProperty: 179;
        生成restriction: 523
      </el-descriptions-item>
    </el-descriptions>

    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="dialogFormVisible2 = false">
          Confirm
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { Timer } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
export default {
  name: 'Model',
  components: { Timer, reactive, ref },
  data() {
    return {
      tableData: [
        {
          index: 1,
          sysml: 'SysML-416.xml',
          owl: 'Ontology-416.owl',
          user: 'admin',
          status: false,
          date: '2023-11-12',
        },
        {
          index: 2,
          sysml: 'SysML-420.xml',
          owl: 'Ontology-420.owl',
          user: 'admin',
          status: false,
          date: '2023-11-13',
        },
        {
          index: 3,
          sysml: 'SysML-625.xml',
          owl: 'Ontology-625.owl',
          user: 'admin',
          status: false,
          date: '2023-11-12',
        },
      ],
      input: '',
      dialogFormVisible: false,
      dialogFormVisible2: false,
      formLabelWidth: '140px',
      form: {
        name: 'Ontology-416.owl',
        datasource: '',
      },
      options: [
        {
          value: 'MES',
          label: 'MES',
        },
        {
          value: 'ERP',
          label: 'ERP',
        },
        {
          value: 'PDM',
          label: 'PDM',
        },
        {
          value: 'AGV',
          label: 'AGV',
        },
        {
          value: 'TMS',
          label: 'Tooling Management System',
        },
      ],
    }
  },
  methods: {
    handleEdit(index, row) {
      console.log(index, row)
    },
    handleDelete(index, row) {
      console.log(index, row)
    },
    preview() {
      this.$router.push('/data/preview')
    },
  },
}
</script>
