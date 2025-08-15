import { Link } from 'react-router-dom';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white shadow-lg rounded-lg p-8">
          <div className="mb-8">
            <Link 
              to="/register" 
              className="inline-flex items-center text-blue-600 hover:text-blue-500 mb-4"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Registration
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Terms of Service</h1>
            <p className="mt-2 text-sm text-gray-600">
              Last updated: August 14, 2025
            </p>
          </div>

          <div className="prose prose-blue max-w-none">
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing and using X-University (the "Service"), you accept and agree to be bound by the terms 
              and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
            </p>

            <h2>2. Service Description</h2>
            <p>
              X-University is an educational platform that provides online courses, learning materials, and 
              interactive learning experiences. The platform supports multiple user roles including students, 
              instructors, and administrators.
            </p>

            <h2>3. User Accounts</h2>
            <p>
              To access certain features of the Service, you must create an account. You are responsible for:
            </p>
            <ul>
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Providing accurate and complete information during registration</li>
              <li>Keeping your account information up to date</li>
            </ul>

            <h2>4. User Conduct</h2>
            <p>You agree not to:</p>
            <ul>
              <li>Use the service for any unlawful purpose or to solicit unlawful activity</li>
              <li>Post or transmit content that is offensive, inappropriate, or violates others' rights</li>
              <li>Attempt to gain unauthorized access to other accounts or the service infrastructure</li>
              <li>Interfere with or disrupt the service or servers connected to the service</li>
            </ul>

            <h2>5. Content and Intellectual Property</h2>
            <p>
              All course materials, text, graphics, logos, and other content on X-University are protected by 
              intellectual property laws. Users may access and use this content for educational purposes only.
            </p>

            <h2>6. Privacy</h2>
            <p>
              Your privacy is important to us. Please review our Privacy Policy, which also governs your use 
              of the Service, to understand our practices.
            </p>

            <h2>7. Limitation of Liability</h2>
            <p>
              X-University shall not be liable for any indirect, incidental, special, consequential, or punitive 
              damages resulting from your use of or inability to use the service.
            </p>

            <h2>8. Changes to Terms</h2>
            <p>
              We reserve the right to modify these terms at any time. Changes will be effective immediately 
              upon posting. Your continued use of the service constitutes acceptance of the modified terms.
            </p>

            <h2>9. Termination</h2>
            <p>
              We may terminate or suspend your account and access to the service immediately, without prior 
              notice, for conduct that we believe violates these Terms of Service or is harmful to other users.
            </p>

            <h2>10. Contact Information</h2>
            <p>
              If you have questions about these Terms of Service, please contact us at terms@x-university.com.
            </p>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <Link 
                to="/register" 
                className="text-blue-600 hover:text-blue-500"
              >
                ← Back to Registration
              </Link>
              <Link 
                to="/privacy" 
                className="text-blue-600 hover:text-blue-500"
              >
                Privacy Policy →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
