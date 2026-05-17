import { useEffect, useState, useCallback } from 'react'
import { useGradeStore } from '../store/gradeStore'
import { gradesAPI } from '../api'
import { useToast } from './useToast'

/**
 * Hook for managing the TA grading queue
 * Handles fetching, navigation, and updates
 */
export const useGradeQueue = (examId) => {
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(false)

  const gradeQueue = useGradeStore(s => s.gradeQueue)
  const currentGrade = useGradeStore(s => s.currentGrade)
  const currentIndex = useGradeStore(s => s.currentIndex)
  const setGradeQueue = useGradeStore(s => s.setGradeQueue)
  const nextGradeStore = useGradeStore(s => s.nextGrade)
  const previousGradeStore = useGradeStore(s => s.previousGrade)
  const updateGrade = useGradeStore(s => s.updateGrade)
  const removeFromQueue = useGradeStore(s => s.removeFromQueue)

  // Load initial queue
  useEffect(() => {
    if (examId) {
      loadQueue()
    }
  }, [examId])

  const loadQueue = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await gradesAPI.getQueue(examId, 'pending')
      setGradeQueue(data.grades || [])
    } catch (error) {
      toast.error('Failed to load grading queue')
    } finally {
      setIsLoading(false)
    }
  }, [examId, setGradeQueue, toast])

  const approve = useCallback(
    async (feedback = null) => {
      if (!currentGrade) return

      try {
        await gradesAPI.approveGrade(currentGrade.id, feedback)
        updateGrade(currentGrade.id, { ta_status: 'approved' })
        removeFromQueue(currentGrade.id)
        toast.success('Grade approved!')
        
        if (gradeQueue.length > currentIndex + 1) {
          nextGradeStore()
        }
      } catch (error) {
        toast.error('Failed to approve grade')
      }
    },
    [currentGrade, currentIndex, gradeQueue, updateGrade, removeFromQueue, nextGradeStore, toast]
  )

  const override = useCallback(
    async (newMarks, reason = '') => {
      if (!currentGrade) return

      try {
        await gradesAPI.overrideGrade(currentGrade.id, {
          override_marks: newMarks,
          override_reason: reason,
        })
        updateGrade(currentGrade.id, {
          ta_status: 'overridden',
          marks: newMarks,
          override_reason: reason,
        })
        removeFromQueue(currentGrade.id)
        toast.success('Grade overridden!')
        
        if (gradeQueue.length > currentIndex + 1) {
          nextGradeStore()
        }
      } catch (error) {
        toast.error('Failed to override grade')
      }
    },
    [currentGrade, currentIndex, gradeQueue, updateGrade, removeFromQueue, nextGradeStore, toast]
  )

  return {
    gradeQueue,
    currentGrade,
    currentIndex,
    isLoading,
    nextGrade: nextGradeStore,
    previousGrade: previousGradeStore,
    approve,
    override,
    hasNext: currentIndex < gradeQueue.length - 1,
    hasPrev: currentIndex > 0,
    progress: `${currentIndex + 1} / ${gradeQueue.length}`,
  }
}

export default useGradeQueue
