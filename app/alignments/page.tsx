'use client';
import AlignmentTable, { AlignmentSet } from '@/components/AlignmentTable';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { zodResolver } from '@hookform/resolvers/zod';
import React from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const formSchema = z.object({
  url: z.string({
    required_error: "Please enter URL."
  }),
})

export default function Page() {
  const [alignmentData, setAlignmentData] = React.useState<AlignmentSet[]>([]);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    reValidateMode: "onSubmit",
  })

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    //  { values } will have the 'url' field
    const data = await getData('spapddpt_split', 10);
    setAlignmentData(data);
  };

  return (
    <div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="border-2 rounded-md p-4 space-y-6">
          <FormField
            control={form.control}
            name="url"
            render={({ field }) => (
              <FormItem>
                <FormLabel>URL</FormLabel>
                <FormControl>
                  <div className='flex flex-row'>
                    <Input className='mr-2' placeholder="Enter URL here..." {...field} />
                    <Button type="submit">Submit</Button>
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </form>
      </Form>
      <AlignmentTable alignmentData={alignmentData} />
    </div>
  );
}

async function getData(
  language_code: string,
  n: number,
): Promise<AlignmentSet[]> {
  const promptRes = await fetch(
    `http://localhost:3000/api/get_alignment?language_code=${language_code}&n=${n}`,
    {
      next: { revalidate: 10 },
    },
  );

  if (!promptRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const alignmentArray = await promptRes.json();

  console.log({ alignmentArray });
  return alignmentArray;
}
