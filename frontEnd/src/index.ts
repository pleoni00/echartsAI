import { PetService } from './petService.js';
declare const echarts: any;
declare const jsyaml: any;

const petService = new PetService();

async function displayPets() {
    const petsContainer = document.getElementById('pets-list');
    if (!petsContainer) return;
}

const createWorker = (code: string) => {
    const blob = new Blob([code], { type: 'application/javascript' });
    const worker = new Worker(URL.createObjectURL(blob));
    return worker;
};

document.addEventListener('DOMContentLoaded', () => {
    displayPets();
    let textArea = document.getElementById("textArea") as HTMLTextAreaElement | null;
    const button = document.getElementById("invio") as HTMLTextAreaElement | null;

    textArea!.value = "Give me a bar plot which illustrate animal type cardinality";

    if (button && textArea){
        button.addEventListener('click', async (e) => {
            const configuration: LLMResponse = await petService.sendText(textArea.value);

            configuration.option = handleOption(JSON.parse(configuration.option));
            console.log(configuration);
            // const configuration: LLMResponse = JSON.parse(result.messages[result.messages.length - 1].content);

            let workerResult = await executeWorker(configuration.ww_code, configuration.data);
            let echartsOption: any = replaceRefs(configuration.option, workerResult);
            const chart = echarts.init(document.getElementById('myChart'));
            chart.setOption(echartsOption);
        });
    }
});

// function extractJSON(response: string): LLMResponse {
//   const cleaned = response.replace(/```json\s*([\s\S]*?)\s*```/, '$1');
//   return JSON.parse(cleaned.trim());
// }

function handleOption(option: any): any {
    for (let key in option) {
        if (key === "formatter") {
            delete option.formatter;
            continue;
        } else {
            if (typeof option[key] === "object")
                option[key] = handleOption(option[key])
        }
        return option
    }
}

function replaceRefs(obj: any, data: any): any {
    if (obj && typeof obj === 'object') {
        if (obj.$ref) {
            return data[obj.$ref];
        }
        
        if (Array.isArray(obj)) {
            return obj.map(item => replaceRefs(item, data));
        }
        
        const result: any = {};
        for (const key in obj) {
            result[key] = replaceRefs(obj[key], data);
        }
        return result;
    }
    return obj;
}

function executeWorker(workerCode: string, data: any): Promise<any> {
    return new Promise((resolve, reject) => {
        const worker = createWorker(workerCode);
        
        worker.onmessage = function(e) {
            const result = e.data;
            console.log('Worker output:', result);
            worker.terminate();
            resolve(result);
        };
        
        worker.onerror = function(error) {
            console.error('Worker error:', error);
            worker.terminate();
            reject(error);
        };
        
        worker.postMessage(data);
    });
}

interface LLMResponse {
  called_tools: any[],
  data: any[],
  ww_code: string,
  option: string
}
