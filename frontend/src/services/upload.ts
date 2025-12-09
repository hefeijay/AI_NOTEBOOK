import axios from 'axios'
import { API_BASE_URL } from '@/utils/config'

const uploadClient = axios.create({
  baseURL: `${API_BASE_URL}`,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

export const uploadApi = {
  async uploadImage(file: File): Promise<string> {
    const formData = new FormData()
    formData.append('file', file)
    const resp = await uploadClient.post<{ url: string }>('/upload', formData)
    return resp.data.url
  }
}

