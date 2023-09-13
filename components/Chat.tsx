'use client';

import { useChat } from 'ai/react';
import { Input } from './ui/input';
import { cn } from '@/lib/utils';
import { ScrollArea } from './ui/scroll-area';
import CollapsibleSection from './CollapsibleSection';

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
                    {messages.map((m) => {
                        const isUser = m.role === 'user'
                        return (
                            <div key={m.id} className={cn(isUser ? 'bg-gray-200' : 'bg-gray-100', 'p-2')}>
                                {m.role === 'user' ? 'User: ' : 'AI: '}
                                {m.content}
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
