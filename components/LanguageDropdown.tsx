import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

import useDatabaseInfo from "@/hooks/UseDatabaseInfo"

type Props = {
    onValueChange: (value: string) => void
}

export default function LanguageDropdown({ onValueChange }: Props) {
    const { data, error } = useDatabaseInfo();

    if (error) {
        return <div>Error loading database info</div>;
    }

    return (
        <Select onValueChange={onValueChange}>
            <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Language" />
            </SelectTrigger>
            <SelectContent>
                {!data && <SelectItem value={"loading"} disabled>Loading...</SelectItem>}
                {data && data.map((item) => <SelectItem key={item.name} value={item.name}>{item.name + " (" + item.num_rows + ")"}</SelectItem>)}
            </SelectContent>
        </Select>
    )
}