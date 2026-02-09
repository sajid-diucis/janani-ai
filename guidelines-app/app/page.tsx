import JananiSearch from "@/components/JananiSearch";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-pink-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 py-12">
      <div className="container mx-auto">
        <JananiSearch />
      </div>
    </main>
  );
}
