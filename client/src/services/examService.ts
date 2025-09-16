import api from './api';
import type { Exam, ExamCreate } from '../types';

const examService = {
  // Get all exams
  getAllExams: async (): Promise<Exam[]> => {
    const response = await api.get('/api/exams');
    return response.data;
  },
  
  // Get a single exam by ID
  getExam: async (id: number): Promise<Exam> => {
    const response = await api.get(`/api/exams/${id}`);
    return response.data;
  },
  
  // Create a new exam
  createExam: async (examData: ExamCreate): Promise<Exam> => {
    const response = await api.post('/api/exams', examData);
    return response.data;
  },
  
  // Generate questions for a section
  generateQuestions: async (sectionId: number): Promise<{ message: string }> => {
    const response = await api.post(`/api/exams/sections/${sectionId}/generate-questions`);
    return response.data;
  },
  
  // Get all questions for a section
  getSectionQuestions: async (sectionId: number): Promise<any[]> => {
    const response = await api.get(`/api/exams/sections/${sectionId}/questions`);
    return response.data;
  },

  // Upload a syllabus for a section
  uploadSyllabus: async (sectionId: number, file: File): Promise<{ file_uri: string }> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/api/exams/sections/${sectionId}/upload-syllabus`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export default examService;