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
    private prompT: string = "You are an Echarts expert assistant. " + 
                "Given a list of tools provide the data and the configuration of the Echarts. " +
                "IMPORTANT: You can and should call multiple tools simultaneously in the same request - use parallel tool calls to gather all data efficiently. " +
                "Always prefer making multiple tool calls at once rather than sequential calls. " +
                "Combine datasets from different tools to build comprehensive configurations. " +
                "This is the output format: data (list of array) and configuration (object). " +
                "Work autonomously: never ask the user for information, develop your own strategy using available tools, and deliver only the requested final result."
    // async getAllPets(): Promise<Pet[]> {
    //     return [{id: 1, name: "Sam", "tag": "tag", "weight": 90, "foodWeightGrams": 20}]
    //     // const response = await fetch(`${this.apiUrl}/pets`);
    //     // return response.json();
    // }

    // async getPet(petId: number): Promise<Pet> {
    //     const response = await fetch(`${this.apiUrl}/pets/${petId}`);
    //     return response.json();
    // }

    // async getPetWeight(petId: number): Promise<{id: number, weight: number}> {
    //     const response = await fetch(`${this.apiUrl}/pets/${petId}/weight`);
    //     return response.json();
    // }

    // async createPet(pet: Omit<Pet, 'id'>): Promise<Pet> {
    //     const response = await fetch(`${this.apiUrl}/pets`, {
    //         method: 'POST',
    //         headers: { 'Content-Type': 'application/json' },
    //         body: JSON.stringify(pet)
    //     });
    //     return response.json();
    // }

    async sendText(message: string): Promise<any> {
        const body = {"messages": [
            {"role": "system", "content": this.prompT},
            {"role": "user", "content": message}
        ]}
        const response = await fetch(`${this.apiUrl}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        return response.json();
    }
}

export { PetService, Pet };