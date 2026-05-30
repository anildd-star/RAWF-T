import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Save, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { templatesApi } from '@/api/services/templates'
import { useExercises } from '@/hooks/useDashboard'
import { useAuth } from '@/contexts/AuthContext'
import type { AssignProgramForm, WorkoutDayForm, WorkoutExerciseForm } from '@/types/workout'
import {
  defaultAssignForm,
  detailToAssignForm,
  emptyDay,
  emptyExercise,
  formToTemplatePayload,
  syncExerciseSetReps,
} from '@/utils/workoutFormHelpers'
import SetRepsEditor from '@/components/workout/SetRepsEditor'

export default function WorkoutTemplateEditPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isNew = !id || id === 'new'
  const templateId = isNew ? null : Number(id)

  const { data: exercises = [] } = useExercises()
  const { data: existing } = useQuery({
    queryKey: ['templates', 'workout', templateId],
    queryFn: () => templatesApi.getWorkout(templateId!),
    enabled: templateId != null && !Number.isNaN(templateId),
  })

  const [form, setForm] = useState<AssignProgramForm>(() => ({
    ...defaultAssignForm(),
    is_active: true,
  }))

  useEffect(() => {
    if (existing) setForm(detailToAssignForm(existing))
  }, [existing])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = formToTemplatePayload(form)
      if (isNew) return templatesApi.createWorkout(payload)
      return templatesApi.updateWorkout(templateId!, payload)
    },
    onSuccess: () => {
      toast.success('Şablon kaydedildi')
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      navigate('/admin/templates')
    },
    onError: () => toast.error('Kayıt başarısız'),
  })

  if (user?.role !== 'admin' && user?.role !== 'coach') {
    return <Navigate to="/" replace />
  }

  const addDay = () => setForm((f) => ({ ...f, days: [...f.days, emptyDay(f.days.length)] }))
  const removeDay = (dayIdx: number) =>
    setForm((f) => ({
      ...f,
      days: f.days.filter((_, i) => i !== dayIdx).map((d, i) => ({ ...d, day_order: i })),
    }))

  const updateDay = (dayIdx: number, field: keyof WorkoutDayForm, value: string | number) => {
    setForm((f) => {
      const days = [...f.days]
      days[dayIdx] = { ...days[dayIdx], [field]: value }
      return { ...f, days }
    })
  }

  const updateExercise = (
    dayIdx: number,
    exIdx: number,
    field: keyof WorkoutExerciseForm,
    value: string | number,
  ) => {
    setForm((f) => {
      const days = [...f.days]
      const exs = [...days[dayIdx].exercises]
      exs[exIdx] = { ...exs[exIdx], [field]: value }
      days[dayIdx] = { ...days[dayIdx], exercises: exs }
      return { ...f, days }
    })
  }

  const updateSetReps = (dayIdx: number, exIdx: number, setReps: number[]) => {
    setForm((f) => {
      const days = [...f.days]
      const exs = [...days[dayIdx].exercises]
      exs[exIdx] = syncExerciseSetReps({ ...exs[exIdx], set_reps: setReps })
      days[dayIdx] = { ...days[dayIdx], exercises: exs }
      return { ...f, days }
    })
  }

  const addExercise = (dayIdx: number) => {
    setForm((f) => {
      const days = [...f.days]
      days[dayIdx] = {
        ...days[dayIdx],
        exercises: [...days[dayIdx].exercises, emptyExercise(days[dayIdx].exercises.length)],
      }
      return { ...f, days }
    })
  }

  const removeExercise = (dayIdx: number, exIdx: number) => {
    setForm((f) => {
      const days = [...f.days]
      days[dayIdx] = {
        ...days[dayIdx],
        exercises: days[dayIdx].exercises.filter((_, i) => i !== exIdx),
      }
      return { ...f, days }
    })
  }

  const submit = () => {
    if (!form.name.trim()) {
      toast.error('Şablon adı girin')
      return
    }
    if (!form.days.some((d) => d.exercises.some((e) => e.exercise_id > 0))) {
      toast.error('En az bir hareket ekleyin')
      return
    }
    saveMutation.mutate()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/admin/templates" className="text-slate-400 hover:text-white">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold">
          {isNew ? t('templates.newWorkout') : t('templates.editWorkout')}
        </h1>
      </div>

      <div className="card grid gap-4 sm:grid-cols-2">
        <input
          className="input-field sm:col-span-2"
          placeholder="Şablon adı"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
        />
        <input
          type="number"
          className="input-field"
          min={1}
          max={52}
          value={form.weeks}
          onChange={(e) => setForm({ ...form, weeks: Number(e.target.value) })}
        />
        <textarea
          className="input-field sm:col-span-2 min-h-[80px]"
          placeholder="Açıklama"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </div>

      {form.days.map((day, dayIdx) => (
        <div key={dayIdx} className="card space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              className="input-field"
              value={day.day_name}
              onChange={(e) => updateDay(dayIdx, 'day_name', e.target.value)}
            />
            <input
              className="input-field"
              placeholder="Bölge"
              value={day.body_region}
              onChange={(e) => updateDay(dayIdx, 'body_region', e.target.value)}
            />
            {form.days.length > 1 && (
              <button type="button" onClick={() => removeDay(dayIdx)} className="btn-secondary text-red-400">
                Günü sil
              </button>
            )}
          </div>
          {day.exercises.map((ex, exIdx) => (
            <div key={exIdx} className="grid gap-2 rounded-lg bg-surface-800/50 p-3 sm:grid-cols-6 lg:grid-cols-7">
              <select
                className="input-field sm:col-span-2"
                value={ex.exercise_id || ''}
                onChange={(e) => updateExercise(dayIdx, exIdx, 'exercise_id', Number(e.target.value))}
              >
                <option value={0}>Hareket seçin</option>
                {exercises.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name}
                  </option>
                ))}
              </select>
              <SetRepsEditor setReps={ex.set_reps} onChange={(setReps) => updateSetReps(dayIdx, exIdx, setReps)} />
              <input type="number" className="input-field" placeholder="kg" value={ex.target_weight_kg} onChange={(e) => updateExercise(dayIdx, exIdx, 'target_weight_kg', e.target.value)} />
              <button type="button" onClick={() => removeExercise(dayIdx, exIdx)} className="btn-secondary text-red-400">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          <button type="button" onClick={() => addExercise(dayIdx)} className="btn-secondary text-sm">
            <Plus className="mr-1 inline h-4 w-4" /> Hareket ekle
          </button>
        </div>
      ))}

      <div className="flex gap-3">
        <button type="button" onClick={addDay} className="btn-secondary">
          <Plus className="mr-1 inline h-4 w-4" /> Gün ekle
        </button>
        <button type="button" onClick={submit} disabled={saveMutation.isPending} className="btn-primary">
          <Save className="mr-1 inline h-4 w-4" />
          {saveMutation.isPending ? t('common.loading') : t('common.save')}
        </button>
      </div>
    </div>
  )
}
