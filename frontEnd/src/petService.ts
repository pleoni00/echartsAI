interface Pet {
    id: number;
    name: string;
    tag: string;
    weight: number;
    foodWeightGrams: number;
}

export interface LLMResponse {
    data: [];
    options: any;
    code: string;
}

class PetService {
    private apiUrl: string = 'http://localhost:8000';
    private prompT?: string; 
    constructor (){
        const pino = async () => {
            const response = await fetch("/public/prompt.md");
            if (!response.ok) {
                throw new Error(`Failed to load prompt: ${response.status}`);
            }
            this.prompT = await response.text();
        }
        pino();
    }

    async sendText(message: string): Promise<any> {
        const body = {"messages": [
            {"role": "system", "content": this.prompT},
            {"role": "user", "content": message}
        ]}
        const response = await fetch(`http://localhost:8000`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        return response.json();
    }
}

export { PetService, Pet };