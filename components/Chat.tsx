'use client';

import { useChat } from 'ai/react';
import { Input } from './ui/input';
import { cn } from '@/lib/utils';
import { ScrollArea } from './ui/scroll-area';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/lib/types';
import { VerseData } from './DemoForm';
import useTargetTokens, { getStrippedToken } from '@/hooks/UseTargetTokens';
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command"

type Props = {
    verseData: VerseData | undefined;
    similarVerses: QueryObject[] | undefined;
    initialInput?: string;
}

export default function Chat({ verseData, similarVerses, initialInput }: Props) {
    const { messages, input, handleInputChange, handleSubmit } = useChat({
        initialInput
    });

    const { availableTokens } = useTargetTokens({ similarVerses, verseData });

    return (
        <CollapsibleSection headerText="Chat">
            <div className="flex flex-col md:flex-row">
                <div className="rounded-md border md:w-2/3">
                    <ScrollArea className="h-[600px] p-4">
                        {messages.map((message) => {
                            const isUserMessage = message.role === 'user';
                            return (
                                <div key={message.id} className={cn(isUserMessage ? 'bg-gray-200' : 'bg-gray-100', 'p-2')}>
                                    <p className="font-bold">{message.role === 'user' ? 'User' : 'AI'}</p>
                                    <div className="flex flex-row flex-wrap gap-x-1 break-words">
                                        {isUserMessage
                                            ? message.content
                                            : message.content?.split(' ').map((token, index) => {
                                                const tokenExists = availableTokens?.includes(getStrippedToken(token));
                                                return (
                                                    <span key={index} className={cn(tokenExists ? 'bg-green-200' : 'bg-yellow-200')}>
                                                        {token}
                                                    </span>
                                                )
                                            })
                                        }
                                    </div>
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
                <Command className="flex rounded-lg border shadow-md md:w-1/3">
                    <CommandInput placeholder="Search for a token..." />
                    <CommandList>
                        <CommandEmpty>No results found.</CommandEmpty>
                        <CommandGroup heading="Available Tokens">
                            {availableTokens && availableTokens.map((token, index) => (
                                <CommandItem key={token}>
                                    <span>{token}</span>
                                </CommandItem>
                            ))}
                        </CommandGroup>
                    </CommandList>
                </Command>
            </div>
        </CollapsibleSection>
    )
}
