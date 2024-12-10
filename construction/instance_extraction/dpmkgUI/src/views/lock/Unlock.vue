<template>
  <h1 class="title">
    ⚡ {{ $t('topbar.lock-locked') }}
    <div class="unlock-btn" @click="handleUnlock">
      <i class="el-icon-unlock"></i>
      {{ $t('topbar.lock-lock') }}
    </div>
  </h1>
  <div class="unlock-modal" v-show="showModal">
    <Avatar class="userinfo-unlock" />
    <el-form :model="lockModel" :rules="lockRules" ref="lockForm">
      <el-form-item prop="password">
        <el-input
          type="password"
          v-model.trim="lockModel.password"
          autocomplete="off"
          :placeholder="$t('topbar.lock-rules-password2')"
          @keyup.enter="submitForm"
          style="width:320px"
        >
          <template #append>
            <el-button
              type="primary"
              class="btn-unlock"
              icon="Right"
              :loading="loading"
              @click="submitForm"
            ></el-button>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item>
        <el-button @click="cancel" type="text">
          {{ $t('public.cancel') }}
        </el-button>
        <el-button @click="reLogin" type="text">
          {{ $t('topbar.lock-relogin') }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
import { defineComponent, ref, reactive, getCurrentInstance } from 'vue'
import Avatar from '@/components/Avatar/index.vue'
import { AesEncryption } from '@/utils/encrypt'
import { useRoute, useRouter } from 'vue-router'
import { Login } from '@/api/login'
import { useApp } from '@/pinia/modules/app'
import { storeToRefs } from 'pinia'
import { useAccount } from '@/pinia/modules/account'

export default defineComponent({
  components: {
    Avatar,
  },
  setup() {
    const { proxy: ctx } = getCurrentInstance()
    const router = useRouter()
    const route = useRoute()
    const showModal = ref(false)
    const lockForm = ref(null)
    const lockModel = reactive({
      password: '',
    })
    const loading = ref(false)

    const appStore = useApp()
    const { authorization } = storeToRefs(appStore)
    const { clearToken, setScreenCode } = appStore
    const accountStore = useAccount()
    const { userinfo } = storeToRefs(accountStore)
    const { getUserinfo } = accountStore

    const checkPwd = async (rule, value, callback) => {
      const cipher = authorization.value && authorization.value.screenCode
      if (!cipher) {
        return callback()
      }
      const pwd = new AesEncryption().decryptByAES(cipher)
      if (pwd === value) {
        return callback()
      } else {
        // 尝试登录
        loading.value = true
        const { code } = await Login({
          username: userinfo.value.name,
          password: value,
        })
        loading.value = false
        if (+code === 200) {
          return callback()
        }
      }
      return callback(new Error(rule.message))
    }

    const lockRules = reactive({
      password: [
        { required: true, message: ctx.$t('topbar.lock-rules-password2') },
        {
          validator: checkPwd,
          message: ctx.$t('topbar.lock-rules-password3'),
          trigger: 'none',
        },
      ],
    })

    const handleUnlock = () => {
      // 判断当前是否登录
      if (authorization.value) {
        showModal.value = true
        // 尝试获取用户信息
        if (!userinfo.value) {
          getUserinfo()
        }
      } else {
        ctx.$message(ctx.$t('topbar.lock-error'))
        reLogin()
      }
    }

    const submitForm = () => {
      lockForm.value.validate(async valid => {
        if (!valid) {
          return false
        }

        // 返回锁屏前的页面
        router.push({ path: route.query.redirect || '/', replace: true })
        // 清除锁屏密码
        setScreenCode('')
      })
    }

    const cancel = () => {
      lockForm.value.resetFields()
      showModal.value = false
    }

    const reLogin = () => {
      router.push('/login?redirect=' + (route.query.redirect || '/'))
      // 清除token
      clearToken()
    }

    return {
      showModal,
      lockForm,
      lockModel,
      lockRules,
      handleUnlock,
      submitForm,
      loading,
      cancel,
      reLogin,
    }
  },
})
</script>

<style lang="scss" scoped>
.title {
  color: #fff;
  text-align: center;
  font-size: 32px;
  margin: 0;
  display: flex;
  align-items: flex-end;
  .unlock-btn {
    color: #aaa;
    font-size: 16px;
    font-weight: normal;
    margin-left: 10px;
    cursor: pointer;
  }
}
.unlock-modal {
  position: fixed;
  z-index: 10;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  ::v-deep(.el-input-group__append) {
    background: $mainColor !important;
    border-color: $mainColor !important;
  }

  .btn-unlock {
    background: $mainColor !important;
    color: #fff !important;
    ::v-deep(i) {
      transform: scale(1.5);
    }
  }
}
.userinfo-unlock {
  margin-bottom: 16px;
  ::v-deep(h3) {
    color: #fff;
  }
}
</style>
