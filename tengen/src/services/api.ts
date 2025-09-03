import axios from 'axios';

export const scrapeResearch = async(topic: string) => {
    try {
        const response = await axios.post('http://localhost:8000/scrape', {topic});
        return response.data;
    } catch (error) {
        console.error('API error', error);
        throw error;
    }
}