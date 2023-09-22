'use client';

import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import CollapsibleSection from './CollapsibleSection';
import { QueryObject } from '@/lib/types';
import { VerseData } from './DemoForm';
import useTargetTokens from '@/hooks/UseTargetTokens';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import ChatMessage from './ChatMessage';
import { Message } from 'ai';
import { ChangeEvent } from 'react';
import { Button } from './ui/button';
import { SendHorizontal, Trash } from 'lucide-react';

type Props = {
  error: Error | undefined;
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  input: string;
  handleInputChange: (
    e: ChangeEvent<HTMLInputElement> | ChangeEvent<HTMLTextAreaElement>,
  ) => void;
  handleSubmit: any;
  verseData: VerseData | undefined;
  similarVerses: QueryObject[] | undefined;
};

export default function Chat({
  error,
  messages,
  setMessages,
  input,
  handleInputChange,
  handleSubmit,
  verseData,
  similarVerses,
}: Props) {
  const { availableTokens } = useTargetTokens({ similarVerses, verseData });

  return (
    <CollapsibleSection headerText="Chat">
      {error && (
        <div>
          <p className="text-red-500">{error.message}</p>
        </div>
      )}
      {verseData?.target?.content && (
        <div>
          <p>{`Expected target output: ${verseData?.target.content}`}</p>
        </div>
      )}
      <div className="flex flex-col md:flex-row gap-2 mt-2">
        <div className="rounded-md border md:w-3/4 h-[600px]">
          <ScrollArea className="h-[600px] p-4">
            {messages.map((message, idx) => (
              <ChatMessage
                key={message.id}
                messageIndex={idx}
                messages={messages}
                availableTokens={availableTokens}
              />
            ))}
          </ScrollArea>
          <form onSubmit={handleSubmit}>
            <div className="flex flex-row gap-x-4">
              <div className="w-full flex flex-row border-2 rounded-md p-1">
                <Input
                  className="border-none focus-visible:outline-none focus-visible:ring-offset-0"
                  placeholder="Send a message"
                  value={input}
                  onChange={handleInputChange}
                />
                <button type="submit">
                  <SendHorizontal color="gray" size={24} />
                </button>
              </div>
              <button onClick={() => setMessages([])}>
                <Trash color="gray" size={24} />
              </button>
            </div>
          </form>
        </div>
        <Command className="flex rounded-lg border shadow-md md:w-1/4 h-[600px]">
          <CommandInput placeholder="Search for a token..." />
          <CommandList>
            <CommandEmpty>No results found.</CommandEmpty>
            <CommandGroup heading="Available Tokens">
              {availableTokens &&
                availableTokens.map((token, index) => (
                  <CommandItem key={token}>
                    <span>{token}</span>
                  </CommandItem>
                ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </div>
    </CollapsibleSection>
  );
}
