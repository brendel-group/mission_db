import React from "react";

interface AbstractPageProps {
  headline: string;
  children: React.ReactNode;
}

export default function AbstractPage({ headline, children }: AbstractPageProps) {
  return (
    <div>
      <h1
        style={{ marginTop: "0px", fontSize: "1.5rem", fontWeight: "normal" }}
      >
        {headline}
      </h1>
      <div>{children}</div>
    </div>
  );
}