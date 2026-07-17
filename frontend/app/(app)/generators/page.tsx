import { PageHeader } from "@/components/page-header";
import { PasswordGenerator } from "@/features/generators/password-generator";
import {
  ApiKeyGenerator,
  JwtSecretGenerator,
  NanoIdGenerator,
  RandomBytesGenerator,
  UuidGenerator,
} from "@/features/generators/simple-generators";
import { EntropyEstimator } from "@/features/generators/entropy-estimator";

export default function GeneratorsPage() {
  return (
    <div>
      <PageHeader title="Generators" description="Cryptographically secure values, generated server-side" />
      <div className="grid gap-4 p-4 md:grid-cols-2 md:p-6">
        <PasswordGenerator />
        <UuidGenerator />
        <NanoIdGenerator />
        <RandomBytesGenerator />
        <ApiKeyGenerator />
        <JwtSecretGenerator />
        <EntropyEstimator />
      </div>
    </div>
  );
}
