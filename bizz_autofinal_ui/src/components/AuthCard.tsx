import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

interface AuthCardProps {
  title: string;
  description: string;
  children: ReactNode;
}

const AuthCard = ({ title, description, children }: AuthCardProps) => {
  return (
    <div
    className="min-h-screen w-full flex items-center justify-center p-4 bg-app-gradient"
 >
      <Card
  className="
    w-full max-w-md rounded-2xl shadow-xl backdrop-blur-md p-6

    bg-white/80 border border-gray-200
    dark:bg-[#0f172a]/60 dark:border-gray-700 dark:shadow-[0_0_10px_rgba(0,0,0,0.4)]
  "
>

        <CardHeader className="text-center space-y-2 pb-2">
          <div className="flex items-center justify-center gap-2 mb-1">
            <Sparkles className="h-7 w-7 text-blue-600" />
            <CardTitle className="text-2xl font-bold text-blue-600">{title}</CardTitle>
          </div>

          <CardDescription className="text-sm text-gray-600">{description}</CardDescription>
        </CardHeader>

        <CardContent className="mt-2 space-y-4">
          {children}
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthCard;
