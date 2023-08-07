import { Configuration, OpenAIApi } from 'openai-edge'
import { OpenAIStream, StreamingTextResponse } from 'ai'
import settings from '@/project_settings.json'


// Create an OpenAI API client (that's edge friendly!)
const config = new Configuration({
    basePath: 'http://localhost:1234/v1'
})
const openai = new OpenAIApi(config)

// IMPORTANT! Set the runtime to edge
export const runtime = 'edge'

export async function POST(req: Request) {
    // Extract the `prompt` from the body of the request
    const { prompt } = await req.json()
    console.log("Using completion with stop_strings:", settings.stop_strings)
    // Ask OpenAI for a streaming completion given the prompt
    const response = await openai.createCompletion({
        model: 'text-davinci-003',
        stream: true,
        prompt,
        stop: settings.stop_strings,
    })

    // Check for errors
    if (!response.ok) {
        return new Response(await response.text(), {
            status: response.status
        })
    }

    // Convert the response into a friendly text-stream
    const stream = OpenAIStream(response)

    // Respond with the stream
    return new StreamingTextResponse(stream)
}