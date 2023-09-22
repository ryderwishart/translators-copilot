'use client';
import AlignmentTable, { AlignmentSet } from '@/components/AlignmentTable';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { zodResolver } from '@hookform/resolvers/zod';
import React from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

const formSchema = z.object({
  filename: z
    .string({
      required_error: 'Please enter filename.',
    })
    .default(''),
});

export default function Page() {
  const [alignmentData, setAlignmentData] = React.useState<AlignmentSet[]>([]);
  const [allAlignmentFiles, setAllAlignmentFiles] = React.useState<string[]>(
    [],
  );

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    reValidateMode: 'onSubmit',
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    const filename = values.filename;
    const alignmentArray = await getAlignmentData(filename, 10);

    setAlignmentData(alignmentArray);
  };

  React.useEffect(() => {
    const fetchFiles = async () => {
      const files = await getAllAlignmentFiles();
      setAllAlignmentFiles(files);
    };

    fetchFiles();
  }, []);

  return (
    <div>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="border-2 rounded-md p-4 space-y-6"
        >
          <FormField
            control={form.control}
            name="filename"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Filename</FormLabel>
                <FormControl>
                  <div className="flex flex-row gap-2">
                    <Select {...field}>
                      <SelectTrigger className="w-[180px]">
                        <SelectValue placeholder="Enter filename here..." />
                      </SelectTrigger>
                      <SelectContent>
                        {allAlignmentFiles.map((file) => (
                          <SelectItem key={file} value={file}>
                            {file}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
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

async function getAlignmentData(
  filename: string,
  n: number,
): Promise<AlignmentSet[]> {
  const promptRes = await fetch(
    `http://localhost:3000/api/get_alignment?filename=${filename}&n=${n}`,
    {
      next: { revalidate: 10 },
    },
  );

  if (!promptRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const alignmentArray = await promptRes.json();
  return alignmentArray;
}

async function getAllAlignmentFiles(): Promise<string[]> {
  // Get the array of string filenames for the alignment data from http://localhost:3000/api/all_alignment_files
  const allAlignmentFilesRes = await fetch(
    `http://localhost:3000/api/all_alignment_files`,
    {
      next: { revalidate: 10 },
    },
  );

  if (!allAlignmentFilesRes.ok) {
    throw new Error('Failed to fetch data');
  }

  // Await the json() method to get the actual data
  const allAlignmentFiles = await allAlignmentFilesRes.json();
  return allAlignmentFiles;
}
