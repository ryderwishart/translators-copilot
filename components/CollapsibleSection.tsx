import { useState } from "react";
import { ChevronRight, ChevronDown } from 'lucide-react';

type Props = {
    headerText: string;
    children?: React.ReactNode;
    preventCollapse?: boolean;
}

export default function SimilarVersesTable({ headerText, children, preventCollapse }: Props) {
    const [showDetails, setShowDetails] = useState<boolean>(true);

    const toggleShowDetails = () => {
        setShowDetails(!showDetails);
    }

    return (
        <div className="flex flex-col gap-6">
            <div className="flex flex-row">
                {!preventCollapse
                    ? <button onClick={() => toggleShowDetails()}>
                        {showDetails
                            ? <ChevronDown color="gray" size={24} />
                            : <ChevronRight color="gray" size={24} />
                        }
                    </button>
                    : null
                }
                <h1 className="font-bold text-2xl">{headerText}</h1>
            </div>
            {showDetails && children}
        </div>
    )
}