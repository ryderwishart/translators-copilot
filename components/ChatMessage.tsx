'use client';

import { cn } from '@/lib/utils';
import { getStrippedToken } from '@/hooks/UseTargetTokens';
import ReactMarkdown from 'react-markdown';
import { Message } from 'ai';

type Props = {
    messages: Message[];
    messageIndex: number;
    availableTokens: string[] | undefined;
}

export default function Chat({ messages, messageIndex, availableTokens }: Props) {
    const currentMessage = messages[messageIndex];
    const previousMessage = messages[messageIndex - 1];
    const isUserMessage = currentMessage.role === 'user';
    // Currently, this will always highlight the assistant's messages,
    // We need to rethink how we want to handle this.
    const shouldHighlight = currentMessage.role === 'assistant' && previousMessage?.content.includes("");

    return (
        <div className={cn(isUserMessage ? 'bg-gray-200' : 'bg-gray-100', 'p-2')}>
            <p className="font-bold">{isUserMessage ? 'User' : 'AI'}</p>
            {isUserMessage
                ? <ReactMarkdown>{currentMessage.content}</ReactMarkdown>
                : shouldHighlight
                    ? <div className="flex flex-row flex-wrap gap-x-1 break-words">
                        {currentMessage.content?.split(' ').map((token, index) => {
                            const tokenExists = availableTokens?.includes(getStrippedToken(token));
                            return (
                                <span key={index} className={cn(tokenExists ? 'bg-green-200' : 'bg-yellow-200')}>
                                    {token}
                                </span>
                            )
                        })}
                    </div>
                    : <ReactMarkdown>{currentMessage.content}</ReactMarkdown>
            }
        </div>
    );
}
