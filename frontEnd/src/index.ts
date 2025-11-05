import { LLMResponse, PetService } from './petService.js';
declare const echarts: any;

const petService = new PetService();

async function displayPets() {
    const petsContainer = document.getElementById('pets-list');
    if (!petsContainer) return;
}

const createWorker = (code: string) => {
    code = `
        var i = 0;

        function timedCount() {
        i = i + 1;
        postMessage(i);
        setTimeout("timedCount()", 500);
        }

        timedCount();
    `;    
    const blob = new Blob([code], { type: 'application/javascript' });
    return new Worker(URL.createObjectURL(blob));
};

document.addEventListener('DOMContentLoaded', () => {
    displayPets();
    const textArea = document.getElementById("textArea") as HTMLTextAreaElement | null;
    const button = document.getElementById("invio") as HTMLTextAreaElement | null;
    
    if (button && textArea){
        button.addEventListener('click', async (e) => {
            const result: any = await petService.sendText(textArea.value);
            console.log(result)
            const configuration = JSON.parse(extractJSON(result.messages[result.messages.length - 1]));
            delete configuration.configuration.tooltip;
            const chart = echarts.init(document.getElementById('myChart'));
            chart.setOption(configuration.configuration);
            // const worker = createWorker("");
            // worker.onmessage = function(event) {
            //     console.log(event);
            // };
        });
    }
});

function extractJSON(response: string) {
  // Rimuove i blocchi markdown ```json ... ```
  const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
  if (jsonMatch) {
    return JSON.parse(jsonMatch[1]);
  }
  
  // Se non c'è markdown, prova a parsare direttamente
  return JSON.parse(response);
}
