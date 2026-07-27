"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Users, Store, Sprout, Phone, Loader2, AlertTriangle, RefreshCw, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "sonner";
import { useLanguage } from "@/hooks/useLanguage";
import {
  useAdminStats,
  useAdminFarmers,
  useAdminVendors,
  useCreateAdminFarmer,
  useDeleteAdminFarmer,
  useCreateAdminVendor,
  useDeleteAdminVendor,
  useAdminSupportCalls,
} from "@/hooks/useAdmin";
import { formatCurrency } from "@/lib/utils";

// ---------------------------------------------------------------------------
// Skeleton loader
// ---------------------------------------------------------------------------

function AdminSkeleton() {
  return (
    <div className="p-4 space-y-4 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-24 bg-gray-100 rounded-lg" />
        ))}
      </div>
      <div className="h-10 bg-gray-200 rounded" />
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-gray-100 rounded-lg" />
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Error state
// ---------------------------------------------------------------------------

function AdminError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="p-4 space-y-4">
      <Card className="border-red-200 bg-red-50">
        <CardContent className="p-6 text-center space-y-3">
          <AlertTriangle className="h-10 w-10 text-red-500 mx-auto" />
          <p className="font-semibold text-red-700">Access Error</p>
          <p className="text-sm text-red-600">{message}</p>
          <Button variant="outline" onClick={onRetry} size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main content
// ---------------------------------------------------------------------------

export default function AdminContent() {
  const { t } = useLanguage();
  const [showAddFarmer, setShowAddFarmer] = useState(false);
  const [showAddVendor, setShowAddVendor] = useState(false);

  // React Query hooks
  const {
    data: stats,
    isLoading: statsLoading,
    isError: statsError,
    refetch: refetchStats,
  } = useAdminStats();

  const {
    data: farmersData,
    isLoading: farmersLoading,
    isError: farmersError,
    refetch: refetchFarmers,
  } = useAdminFarmers(0, 20);

  const {
    data: vendorsData,
    isLoading: vendorsLoading,
    isError: vendorsError,
    refetch: refetchVendors,
  } = useAdminVendors(0, 20);

  const {
    data: callsData,
    isLoading: callsLoading,
  } = useAdminSupportCalls();

  // Mutations
  const createFarmerMutation = useCreateAdminFarmer();
  const deleteFarmerMutation = useDeleteAdminFarmer();
  const createVendorMutation = useCreateAdminVendor();
  const deleteVendorMutation = useDeleteAdminVendor();

  // Farmer form state
  const [farmerForm, setFarmerForm] = useState({ name: "", phone: "", city: "" });
  // Vendor form state
  const [vendorForm, setVendorForm] = useState({ name: "", vendor_type: "", phone: "", city: "" });

  const handleAddFarmer = async () => {
    if (!farmerForm.name || !farmerForm.phone) {
      toast.error("Name and phone are required");
      return;
    }
    try {
      await createFarmerMutation.mutateAsync({
        name: farmerForm.name,
        phone: farmerForm.phone,
        city: farmerForm.city || undefined,
      });
      toast.success("Farmer added successfully");
      setFarmerForm({ name: "", phone: "", city: "" });
      setShowAddFarmer(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to add farmer";
      toast.error(msg);
    }
  };

  const handleAddVendor = async () => {
    if (!vendorForm.name || !vendorForm.vendor_type || !vendorForm.phone || !vendorForm.city) {
      toast.error("All fields are required");
      return;
    }
    try {
      await createVendorMutation.mutateAsync({
        name: vendorForm.name,
        vendor_type: vendorForm.vendor_type,
        phone: vendorForm.phone,
        city: vendorForm.city,
      });
      toast.success("Vendor added successfully");
      setVendorForm({ name: "", vendor_type: "", phone: "", city: "" });
      setShowAddVendor(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to add vendor";
      toast.error(msg);
    }
  };

  const handleDeleteFarmer = async (id: string, name: string) => {
    if (!confirm(`Deactivate farmer "${name}"?`)) return;
    try {
      await deleteFarmerMutation.mutateAsync(id);
      toast.success(`${name} deactivated`);
    } catch {
      toast.error("Failed to deactivate farmer");
    }
  };

  const handleDeleteVendor = async (id: string, name: string) => {
    if (!confirm(`Deactivate vendor "${name}"?`)) return;
    try {
      await deleteVendorMutation.mutateAsync(id);
      toast.success(`${name} deactivated`);
    } catch {
      toast.error("Failed to deactivate vendor");
    }
  };

  // Loading state
  if (statsLoading || (farmersLoading && vendorsLoading)) return <AdminSkeleton />;

  // Error state (all three failed = likely not admin)
  if (statsError && farmersError && vendorsError) {
    return (
      <AdminError
        message="You do not have admin access. Please log in with an admin account."
        onRetry={() => {
          refetchStats();
          refetchFarmers();
          refetchVendors();
        }}
      />
    );
  }

  const farmers = farmersData?.farmers ?? [];
  const vendors = vendorsData?.vendors ?? [];
  const calls = callsData?.calls ?? [];

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{t("admin.title")}</h1>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            refetchStats();
            refetchFarmers();
            refetchVendors();
          }}
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: "Total Farmers",
            value: stats?.total_farmers ?? 0,
            icon: <Users className="h-5 w-5" />,
            color: "bg-blue-50 text-blue-600",
          },
          {
            label: "Total Vendors",
            value: stats?.total_vendors ?? 0,
            icon: <Store className="h-5 w-5" />,
            color: "bg-green-50 text-green-600",
          },
          {
            label: "Active Crops",
            value: stats?.active_crops ?? 0,
            icon: <Sprout className="h-5 w-5" />,
            color: "bg-amber-50 text-amber-600",
          },
          {
            label: "Call Requests",
            value: calls.length,
            icon: <Phone className="h-5 w-5" />,
            color: "bg-red-50 text-red-600",
          },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <CardContent className="p-4">
                <div className={`flex h-10 w-10 items-center justify-center rounded-lg mb-2 ${stat.color}`}>
                  {stat.icon}
                </div>
                <p className="text-2xl font-bold">{stat.value.toLocaleString()}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Tabs */}
      <Tabs defaultValue="farmers">
        <TabsList className="w-full">
          <TabsTrigger value="farmers" className="flex-1">{t("admin.farmerList")}</TabsTrigger>
          <TabsTrigger value="vendors" className="flex-1">{t("admin.vendorList")}</TabsTrigger>
        </TabsList>

        {/* Farmers Tab */}
        <TabsContent value="farmers" className="space-y-3 mt-4">
          <div className="flex justify-end">
            <Button onClick={() => setShowAddFarmer(true)} className="gap-2">
              + {t("admin.addFarmer")}
            </Button>
          </div>

          {farmersLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : farmers.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No farmers registered yet
              </CardContent>
            </Card>
          ) : (
            farmers.map((farmer) => (
              <Card key={farmer.id}>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-mithrava-100 flex items-center justify-center text-mithrava-600 font-bold text-sm shrink-0">
                    {farmer.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{farmer.name}</p>
                    <p className="text-xs text-gray-500 truncate">
                      {farmer.phone} {farmer.city ? `· ${farmer.city}` : ""}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant={farmer.is_active ? "secondary" : "destructive"}>
                      {farmer.is_active ? farmer.role : "inactive"}
                    </Badge>
                    {farmer.is_active && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteFarmer(farmer.id, farmer.name)}
                        className="text-red-500 hover:text-red-700 h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* Vendors Tab */}
        <TabsContent value="vendors" className="space-y-3 mt-4">
          <div className="flex justify-end">
            <Button onClick={() => setShowAddVendor(true)} className="gap-2">
              + {t("admin.addVendor")}
            </Button>
          </div>

          {vendorsLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : vendors.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                No vendors registered yet
              </CardContent>
            </Card>
          ) : (
            vendors.map((vendor) => (
              <Card key={vendor.id}>
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-amber-100 flex items-center justify-center text-lg shrink-0">
                    🏪
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{vendor.name}</p>
                    <p className="text-xs text-gray-500 truncate">
                      {vendor.vendor_type} · {vendor.city}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {vendor.rating && (
                      <Badge variant="success">⭐ {vendor.rating.toFixed(1)}</Badge>
                    )}
                    <Badge variant={vendor.is_active ? "secondary" : "destructive"}>
                      {vendor.is_active ? "active" : "inactive"}
                    </Badge>
                    {vendor.is_active && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteVendor(vendor.id, vendor.name)}
                        className="text-red-500 hover:text-red-700 h-8 w-8 p-0"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>

      {/* ── Support Calls Section ── */}
      {calls.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Phone className="h-4 w-4" />
                Recent Support Calls ({calls.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {calls.slice(0, 5).map((call) => (
                <div
                  key={call.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-gray-50"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{call.topic}</p>
                    <p className="text-xs text-gray-500 truncate">
                      Farmer: {call.farmer_id.slice(0, 8)}… {call.preferred_time ? `· ${call.preferred_time}` : ""}
                    </p>
                  </div>
                  <Badge
                    variant={
                      call.status === "completed"
                        ? "success"
                        : call.status === "cancelled"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {call.status}
                  </Badge>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* ── Add Farmer Dialog ── */}
      <Dialog open={showAddFarmer} onOpenChange={setShowAddFarmer}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("admin.addFarmer")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Name *</Label>
              <Input
                placeholder="Farmer name"
                className="mt-1.5"
                value={farmerForm.name}
                onChange={(e) => setFarmerForm((p) => ({ ...p, name: e.target.value }))}
              />
            </div>
            <div>
              <Label>Phone *</Label>
              <Input
                placeholder="10-digit phone number"
                className="mt-1.5"
                value={farmerForm.phone}
                onChange={(e) => setFarmerForm((p) => ({ ...p, phone: e.target.value }))}
              />
            </div>
            <div>
              <Label>City</Label>
              <Input
                placeholder="City"
                className="mt-1.5"
                value={farmerForm.city}
                onChange={(e) => setFarmerForm((p) => ({ ...p, city: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddFarmer(false)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={handleAddFarmer} disabled={createFarmerMutation.isPending}>
              {createFarmerMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              {t("common.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Add Vendor Dialog ── */}
      <Dialog open={showAddVendor} onOpenChange={setShowAddVendor}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("admin.addVendor")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <Label>Name *</Label>
              <Input
                placeholder="Vendor name"
                className="mt-1.5"
                value={vendorForm.name}
                onChange={(e) => setVendorForm((p) => ({ ...p, name: e.target.value }))}
              />
            </div>
            <div>
              <Label>Type *</Label>
              <Select
                value={vendorForm.vendor_type}
                onValueChange={(val) => setVendorForm((p) => ({ ...p, vendor_type: val }))}
              >
                <SelectTrigger className="mt-1.5">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fertilizer">Fertilizer Dealer</SelectItem>
                  <SelectItem value="pesticide">Pesticide Shop</SelectItem>
                  <SelectItem value="seed">Seed Shop</SelectItem>
                  <SelectItem value="equipment">Equipment Dealer</SelectItem>
                  <SelectItem value="buyer">Buyer / Mandi</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Phone *</Label>
              <Input
                placeholder="10-digit phone number"
                className="mt-1.5"
                value={vendorForm.phone}
                onChange={(e) => setVendorForm((p) => ({ ...p, phone: e.target.value }))}
              />
            </div>
            <div>
              <Label>City *</Label>
              <Input
                placeholder="City"
                className="mt-1.5"
                value={vendorForm.city}
                onChange={(e) => setVendorForm((p) => ({ ...p, city: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAddVendor(false)}>
              {t("common.cancel")}
            </Button>
            <Button onClick={handleAddVendor} disabled={createVendorMutation.isPending}>
              {createVendorMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              {t("common.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
