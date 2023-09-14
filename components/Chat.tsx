'use client';

import { useChat } from 'ai/react';
import { Input } from './ui/input';
import { cn } from '@/lib/utils';
import { ScrollArea } from './ui/scroll-area';
import CollapsibleSection from './CollapsibleSection';
import ReactMarkdown from 'react-markdown';

type Props = {
    initialInput?: string;
}

export default function Chat({ initialInput }: Props) {
    const { messages, input, handleInputChange, handleSubmit } = useChat({
        initialInput
    });

    return (
        <CollapsibleSection headerText="Chat">
            <div className="rounded-md border">
                <ScrollArea className="h-[600px] p-4">
                    {messages.map((message, idx) => {
                        const isUser = message.role === 'user'
                        if (idx === messages.length - 1) console.log(message)
                        return (
                            <div key={message.id} className={cn(isUser ? 'bg-gray-200' : 'bg-gray-100', 'p-2')}>
                                <p className="font-bold">{message.role === 'user' ? 'User' : 'AI'}</p>
                                { /* eslint-disable-next-line react/no-children-prop */ }
                                <ReactMarkdown children={message.content} />
                            </div>
                        )
                    })}
                </ScrollArea>
                <form onSubmit={handleSubmit}>
                    <Input
                        className="border-t-2 p-2 focus-visible:outline-none focus-visible:ring-offset-0"
                        placeholder='Send a message'
                        value={input}
                        onChange={handleInputChange}
                    />
                </form>
            </div>
        </CollapsibleSection>
    )
}
