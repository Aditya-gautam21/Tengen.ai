import axios from 'axios';

export const scrapeResearch = async(topic: string) => {
    try {
        const response = await axios.post('http://localhost:8000/scrape', {topic});
        return response.data;
    } catch (error) {
        console.error('API error', error);
        throw error;
    }
};

export const codeAssist = async (prompt: string, code: string | null, mode: 'generate' | 'debug') => {
    try{
        const response = await axios.post('http://localhost:8000/code-assist', {prompt, code, mode});
        return response.data;
    }catch(error){
        console.error('API error', error);
        throw error;
    }
};